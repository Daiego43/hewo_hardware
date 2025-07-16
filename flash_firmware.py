import yaml
import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Importar el generador de código (asumiendo que está en el mismo directorio)
from ino_generator import InoCodeGenerator

WORKDIR = Path(__file__).parent.absolute()
DEFAULT_CONFIG = WORKDIR / 'neck_config.yaml'
DEFAULT_DEV = "/dev/esp32"
DEFAULT_BAUDRATE = 115200


class FirmwareFlasher:
    """Clase para compilar y subir firmware a ESP32 basado en configuración YAML"""

    def __init__(self, config_file: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else DEFAULT_CONFIG
        self.settings = self._load_settings()
        self.arduino_cli = self._resolve_cli()
        self.board = self.settings['board_settings']
        self.fqbn = self.board['fqbn']
        self.sketch_path = Path(self.board['sketch'])
        self.ino_file = Path(self.board.get('ino_file', f"{self.sketch_path}/{self.sketch_path.name}.ino"))
        self.port = self._resolve_port()
        self.baudrate = self.board.get('baudrate', DEFAULT_BAUDRATE)

        # Inicializar generador de código
        self.code_generator = InoCodeGenerator(str(self.config_file))

    def _load_settings(self) -> Dict[str, Any]:
        """Carga la configuración desde el archivo YAML"""
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Archivo de configuración no encontrado: {self.config_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"❌ Error al parsear YAML: {e}")

    def _resolve_cli(self) -> str:
        """Resuelve la ruta del Arduino CLI"""
        cli_path = self.settings.get('arduino_cli_path')
        if cli_path and cli_path.lower() != "none":
            return cli_path
        return "arduino-cli"

    def _resolve_port(self) -> str:
        """Resuelve el puerto serie para la ESP32"""
        port = self.board.get('port')
        if port and os.path.exists(port):
            return port
        elif os.path.exists(DEFAULT_DEV):
            print(f"🔌 Usando dispositivo detectado: {DEFAULT_DEV}")
            return DEFAULT_DEV
        else:
            # Buscar puertos disponibles
            available_ports = self._find_available_ports()
            if available_ports:
                selected_port = available_ports[0]
                print(f"🔌 Puerto detectado automáticamente: {selected_port}")
                return selected_port
            else:
                raise RuntimeError("❌ No se encontró ningún puerto disponible para ESP32")

    def _find_available_ports(self) -> list:
        """Busca puertos serie disponibles"""
        try:
            result = subprocess.run([self.arduino_cli, "board", "list"],
                                    capture_output=True, text=True, check=True)
            ports = []
            for line in result.stdout.split('\n'):
                if '/dev/tty' in line and ('USB' in line or 'ESP32' in line):
                    port = line.split()[0]
                    ports.append(port)
            return ports
        except subprocess.CalledProcessError:
            return []

    def _run_command(self, args: list, msg: str, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Ejecuta un comando del Arduino CLI"""
        print(msg)
        try:
            return subprocess.run([self.arduino_cli] + args,
                                  check=True,
                                  capture_output=capture_output,
                                  text=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error ejecutando comando: {e}")
            if capture_output and e.stderr:
                print(f"   Stderr: {e.stderr}")
            raise

    def generate_ino(self) -> bool:
        """Genera el código .ino usando el generador mejorado"""
        try:
            print("🔧 Generando código .ino desde configuración YAML...")

            # Mostrar resumen de configuración
            print(self.code_generator.get_servo_summary())

            # Generar archivo
            success = self.code_generator.save_ino_file(str(self.ino_file))

            if success:
                print("✅ Código .ino generado exitosamente")
            return success

        except Exception as e:
            print(f"❌ Error generando código .ino: {e}")
            return False

    def validate_config(self) -> bool:
        """Valida la configuración antes de proceder"""
        try:
            # Validar que existan las secciones principales
            required_sections = ['board_settings', 'servo_settings']
            for section in required_sections:
                if section not in self.settings:
                    print(f"❌ Falta sección '{section}' en configuración")
                    return False

            # Validar configuración de servos
            servo_settings = self.settings['servo_settings']
            if not servo_settings:
                print("❌ No hay servos configurados")
                return False

            # Validar cada servo
            for servo_id, config in servo_settings.items():
                if 'gpio' not in config:
                    print(f"❌ Servo {servo_id}: falta GPIO")
                    return False
                if 'type' not in config:
                    print(f"❌ Servo {servo_id}: falta tipo")
                    return False

            print("✅ Configuración válida")
            return True

        except Exception as e:
            print(f"❌ Error validando configuración: {e}")
            return False

    def compile(self) -> bool:
        """Compila el sketch"""
        try:
            self._run_command(["compile", "--fqbn", self.fqbn, str(self.sketch_path)],
                              f"📦 Compilando sketch en {self.sketch_path} para {self.fqbn}...")
            print("✅ Compilación exitosa")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error en compilación")
            return False

    def upload(self) -> bool:
        """Sube el firmware a la ESP32"""
        try:
            self._run_command(["upload", "-p", self.port, "--fqbn", self.fqbn, str(self.sketch_path)],
                              f"⚡ Subiendo firmware a {self.port}...")
            print("✅ Firmware subido exitosamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error subiendo firmware")
            return False

    def flash(self) -> bool:
        """Proceso completo: validar, generar, compilar y subir"""
        try:
            # Validar configuración
            if not self.validate_config():
                return False

            # Generar código .ino
            if not self.generate_ino():
                return False

            # Compilar
            if not self.compile():
                return False

            # Subir
            if not self.upload():
                return False

            print("🎉 Proceso completo exitoso!")
            return True

        except Exception as e:
            print(f"❌ Error en proceso de flash: {e}")
            return False

    def monitor(self) -> None:
        """Abre el monitor serie"""
        try:
            print(f"🔍 Abriendo monitor serie en {self.port}...")
            subprocess.run([self.arduino_cli, "monitor", "-p", self.port,
                            "--baudrate", str(self.baudrate)])
        except KeyboardInterrupt:
            print("\n📴 Monitor serie cerrado")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error abriendo monitor: {e}")

    def show_settings(self) -> None:
        """Muestra la configuración actual"""
        print("🔧 Configuración actual:")
        print(f"   📁 Config file:  {self.config_file}")
        print(f"   📝 Sketch:       {self.sketch_path}")
        print(f"   📄 Ino file:     {self.ino_file}")
        print(f"   🏷️  FQBN:        {self.fqbn}")
        print(f"   🔌 Port:         {self.port}")
        print(f"   📡 Baudrate:     {self.baudrate}")
        print(f"   🛠️  CLI path:     {self.arduino_cli}")
        print()

        # Mostrar configuración de servos
        print(self.code_generator.get_servo_summary())

    def restore_backup(self) -> bool:
        """Restaura el archivo .ino desde el backup"""
        backup_file = Path(f"{self.ino_file}.backup")

        if backup_file.exists():
            try:
                with open(backup_file, 'r') as f:
                    backup_content = f.read()

                with open(self.ino_file, 'w') as f:
                    f.write(backup_content)

                print(f"🔄 Archivo {self.ino_file} restaurado desde backup")
                return True
            except Exception as e:
                print(f"❌ Error restaurando backup: {e}")
                return False
        else:
            print(f"❌ No se encontró archivo de backup: {backup_file}")
            return False

    def clean(self) -> bool:
        """Limpia archivos temporales de compilación"""
        try:
            # Limpiar directorio de build
            build_dir = self.sketch_path / "build"
            if build_dir.exists():
                import shutil
                shutil.rmtree(build_dir)
                print(f"🧹 Directorio de build limpiado: {build_dir}")

            # Limpiar archivos temporales
            temp_files = list(self.sketch_path.glob("*.tmp"))
            for temp_file in temp_files:
                temp_file.unlink()
                print(f"🧹 Archivo temporal eliminado: {temp_file}")

            print("✅ Limpieza completada")
            return True

        except Exception as e:
            print(f"❌ Error durante limpieza: {e}")
            return False

    def check_dependencies(self) -> bool:
        """Verifica que todas las dependencias estén instaladas"""
        try:
            # Verificar Arduino CLI
            result = self._run_command(["version"], "🔍 Verificando Arduino CLI...", capture_output=True)
            print(f"   Arduino CLI: {result.stdout.strip()}")

            # Verificar que el core ESP32 esté instalado
            result = self._run_command(["core", "list"], "🔍 Verificando cores instalados...", capture_output=True)
            if "esp32:esp32" not in result.stdout:
                print("⚠️  Core ESP32 no encontrado. Instalando...")
                self._run_command(["core", "install", "esp32:esp32"], "📦 Instalando core ESP32...")

            # Verificar librerías necesarias
            result = self._run_command(["lib", "list"], "🔍 Verificando librerías...", capture_output=True)
            if "ESP32Servo" not in result.stdout:
                print("⚠️  Librería ESP32Servo no encontrada. Instalando...")
                self._run_command(["lib", "install", "ESP32Servo"], "📦 Instalando ESP32Servo...")

            print("✅ Todas las dependencias están instaladas")
            return True

        except subprocess.CalledProcessError:
            print("❌ Error verificando dependencias")
            return False

    def create_project_structure(self) -> bool:
        """Crea la estructura de directorios del proyecto"""
        try:
            # Crear directorio del sketch
            self.sketch_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Directorio del sketch: {self.sketch_path}")

            # Crear archivo .ino si no existe
            if not self.ino_file.exists():
                print(f"📝 Creando archivo .ino: {self.ino_file}")
                # El archivo se creará cuando se genere el código

            return True

        except Exception as e:
            print(f"❌ Error creando estructura del proyecto: {e}")
            return False

    def __repr__(self) -> str:
        return f"<FirmwareFlasher sketch='{self.sketch_path}' port='{self.port}' fqbn='{self.fqbn}'>"


def main():
    """Función principal para uso desde línea de comandos"""
    import argparse

    parser = argparse.ArgumentParser(description="Generador y flasher de firmware para ESP32")
    parser.add_argument("command", nargs='?', default="flash",
                        choices=["flash", "compile", "upload", "monitor", "settings",
                                 "generate", "restore", "clean", "check-deps", "init"],
                        help="Comando a ejecutar")
    parser.add_argument("-c", "--config", type=str, default=None,
                        help="Archivo de configuración YAML (por defecto: neck_config.yaml)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Salida detallada")

    args = parser.parse_args()

    try:
        # Crear instancia del flasher
        flasher = FirmwareFlasher(args.config)

        # Ejecutar comando
        if args.command == "flash":
            success = flasher.flash()
        elif args.command == "compile":
            success = flasher.generate_ino() and flasher.compile()
        elif args.command == "upload":
            success = flasher.upload()
        elif args.command == "monitor":
            flasher.monitor()
            success = True
        elif args.command == "settings":
            flasher.show_settings()
            success = True
        elif args.command == "generate":
            success = flasher.generate_ino()
        elif args.command == "restore":
            success = flasher.restore_backup()
        elif args.command == "clean":
            success = flasher.clean()
        elif args.command == "check-deps":
            success = flasher.check_dependencies()
        elif args.command == "init":
            success = flasher.create_project_structure()
        else:
            print("❓ Comando no reconocido")
            success = False

        # Mostrar resultado
        if success:
            print("🎉 Comando ejecutado exitosamente")
            sys.exit(0)
        else:
            print("💥 El comando falló")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()