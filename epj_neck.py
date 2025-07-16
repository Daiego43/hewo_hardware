import serial
import time
import threading
from typing import List, Optional, Union


class ESP32NeckController:
    """
    Wrapper de Python para controlar el sistema de servos del cuello ESP32.

    Comandos disponibles:
    - V: Control PWM directo
    - A: Control por ángulos con temporización automática
    - T: Test de servo individual
    - C: Calibración de velocidad
    - P: Consultar posiciones actuales
    - R: Reset de posiciones
    - D: Toggle modo debug
    - S: Stop inmediato
    - I: Info del sistema
    """

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        """
        Inicializa la conexión serie con el ESP32.

        Args:
            port: Puerto serie (ej: 'COM3', '/dev/ttyUSB0')
            baudrate: Velocidad de comunicación (default: 115200)
            timeout: Timeout para operaciones serie (default: 1.0s)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.is_connected = False
        self.num_servos = 3  # Según tu configuración

    def connect(self) -> bool:
        """
        Establece la conexión serie con el ESP32.

        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # Esperar a que el ESP32 se reinicie
            self.is_connected = True
            print(f"✅ Conectado a {self.port} a {self.baudrate} baudios")
            return True
        except Exception as e:
            print(f"❌ Error conectando a {self.port}: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """Cierra la conexión serie."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.is_connected = False
            print("🔌 Desconectado")

    def _send_command(self, command: str) -> bool:
        """
        Envía un comando al ESP32.

        Args:
            command: Comando a enviar

        Returns:
            bool: True si el comando se envió correctamente
        """
        if not self.is_connected or not self.serial_connection:
            print("❌ No hay conexión establecida")
            return False

        try:
            self.serial_connection.write(f"{command}\n".encode())
            self.serial_connection.flush()
            return True
        except Exception as e:
            print(f"❌ Error enviando comando '{command}': {e}")
            return False

    def set_pwm(self, pwm_values: List[Union[int, float]]) -> bool:
        """
        Establece valores PWM directos para todos los servos.

        Args:
            pwm_values: Lista de valores PWM (0-180) para cada servo

        Returns:
            bool: True si el comando se envió correctamente

        Example:
            controller.set_pwm([95, 120, 80])  # Servo 1 parado, 2 girando CW, 3 girando CCW
        """
        if len(pwm_values) != self.num_servos:
            print(f"❌ Se esperaban {self.num_servos} valores PWM, se recibieron {len(pwm_values)}")
            return False

        # Validar rango PWM
        for i, pwm in enumerate(pwm_values):
            if not (0 <= pwm <= 180):
                print(f"❌ PWM fuera de rango para servo {i + 1}: {pwm} (debe estar entre 0-180)")
                return False

        pwm_str = " ".join(map(str, pwm_values))
        command = f"V {pwm_str}"
        return self._send_command(command)

    def move_angles(self, angles: List[Union[int, float]]) -> bool:
        """
        Mueve los servos por ángulos específicos con temporización automática.

        Args:
            angles: Lista de ángulos relativos para cada servo (positivo = CW, negativo = CCW)

        Returns:
            bool: True si el comando se envió correctamente

        Example:
            controller.move_angles([45, -30, 90])  # Servo 1: +45°, Servo 2: -30°, Servo 3: +90°
        """
        if len(angles) != self.num_servos:
            print(f"❌ Se esperaban {self.num_servos} ángulos, se recibieron {len(angles)}")
            return False

        angles_str = " ".join(map(str, angles))
        command = f"A {angles_str}"
        return self._send_command(command)

    def test_servo(self, servo_num: int, angle: Union[int, float]) -> bool:
        """
        Prueba un servo individual con un ángulo específico.

        Args:
            servo_num: Número del servo (1-3)
            angle: Ángulo relativo a mover

        Returns:
            bool: True si el comando se envió correctamente

        Example:
            controller.test_servo(1, 45)  # Mueve servo 1 por 45°
        """
        if not (1 <= servo_num <= self.num_servos):
            print(f"❌ Servo inválido: {servo_num} (debe estar entre 1-{self.num_servos})")
            return False

        command = f"T {servo_num} {angle}"
        return self._send_command(command)

    def calibrate_speed(self, factor: float) -> bool:
        """
        Ajusta el factor de calibración de velocidad.

        Args:
            factor: Factor de calibración (0.1-5.0)

        Returns:
            bool: True si el comando se envió correctamente

        Example:
            controller.calibrate_speed(1.5)  # Movimientos 50% más lentos
        """
        if not (0.1 <= factor <= 5.0):
            print(f"❌ Factor de calibración fuera de rango: {factor} (debe estar entre 0.1-5.0)")
            return False

        command = f"C {factor}"
        return self._send_command(command)

    def get_positions(self) -> bool:
        """
        Solicita las posiciones actuales de todos los servos.

        Returns:
            bool: True si el comando se envió correctamente
        """
        return self._send_command("P")

    def reset_positions(self) -> bool:
        """
        Reinicia todas las posiciones a 0°.

        Returns:
            bool: True si el comando se envió correctamente
        """
        return self._send_command("R")

    def toggle_debug(self) -> bool:
        """
        Activa/desactiva el modo debug.

        Returns:
            bool: True si el comando se envió correctamente
        """
        return self._send_command("D")

    def stop_all(self) -> bool:
        """
        Detiene inmediatamente todos los servos.

        Returns:
            bool: True si el comando se envió correctamente
        """
        return self._send_command("S")

    def get_system_info(self) -> bool:
        """
        Solicita información del sistema.

        Returns:
            bool: True si el comando se envió correctamente
        """
        return self._send_command("I")

    def __enter__(self):
        """Soporte para context manager."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Soporte para context manager."""
        self.disconnect()


# Funciones de conveniencia para movimientos comunes
class NeckMovements:
    """Clase con movimientos predefinidos para el cuello."""

    def __init__(self, controller: ESP32NeckController):
        self.controller = controller

    def nod_yes(self, intensity: float = 30) -> bool:
        """
        Movimiento de asentimiento (sí).

        Args:
            intensity: Intensidad del movimiento en grados
        """
        return self.controller.move_angles([intensity, 0, 0])

    def shake_no(self, intensity: float = 30) -> bool:
        """
        Movimiento de negación (no).

        Args:
            intensity: Intensidad del movimiento en grados
        """
        return self.controller.move_angles([0, intensity, 0])

    def tilt_head(self, intensity: float = 30) -> bool:
        """
        Inclinar la cabeza hacia un lado.

        Args:
            intensity: Intensidad del movimiento en grados
        """
        return self.controller.move_angles([0, 0, intensity])

    def center_all(self) -> bool:
        """Centra todos los servos."""
        return self.controller.reset_positions()

    def look_around(self, pan: float = 45, tilt: float = 20) -> bool:
        """
        Movimiento de "mirar alrededor".

        Args:
            pan: Movimiento horizontal
            tilt: Movimiento de inclinación
        """
        return self.controller.move_angles([tilt, pan, 0])


def test_servos():
    with ESP32NeckController("/dev/esp32") as controller:
        for servo in range(3):
            print(f"Moving Servo {servo + 1}")
            a = 45
            for angle in [ a,  a, -a, -a,
                          -a, -a,  a,  a]:
                angles = [0, 0, 0]
                angles[servo] = angle
                controller.move_angles(angles)
                time.sleep(0.3)

def test_velocities():
    with ESP32NeckController("/dev/esp32") as controller:
        ccw_min_vel = 90
        ccw_max_vel = 40
        print("Moving counter clock wise")
        for velocity in range(ccw_min_vel, ccw_max_vel, -1):
            controller.set_pwm([velocity,velocity,velocity])
            time.sleep(0.1)
        for velocity in range(ccw_max_vel, ccw_min_vel, 1):
            controller.set_pwm([velocity,velocity,velocity])
            time.sleep(0.1)
        print("Stop")
        controller.stop_all()
        time.sleep(0.5)
        cw_min_vel = 97
        cw_max_vel = 150
        print("Moving clock wise")
        for velocity in range(cw_min_vel, cw_max_vel, 1):
            controller.set_pwm([velocity,velocity,velocity])
            time.sleep(0.1)
        for velocity in range(cw_max_vel, cw_min_vel, -1):
            controller.set_pwm([velocity,velocity,velocity])
            time.sleep(0.1)
        controller.stop_all()




if __name__ == '__main__':
    test_servos()
    test_velocities()