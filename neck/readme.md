# Control de Cuello EPJ con ESP32-S3 y 3 Servos

Este módulo contiene el firmware y scripts necesarios para controlar un cuello Esférico Paralelo (EPJ) utilizando un microcontrolador ESP32-S3 y tres servomotores. El sistema está alimentado por una fuente de 12 V conectada a una breakout board.

## 🧰 Hardware necesario

- **Microcontrolador:** ESP32-S3  
- **Breakout board** compatible con ESP32-S3  
- **Fuente de alimentación:** 12 V DC (para los servos)  
- **3 servomotores** para el cuello EPJ (ej. MG90S)  
- **Cable USB OTG** para flashear  
- **Adaptador USB-UART** (opcional, para comunicación desde PC)  

---

## ⚙️ Instalación de Arduino CLI

### 1. Instalar Arduino CLI

```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
sudo mv bin/arduino-cli /usr/local/bin/
````

### 2. Configurar CLI y soporte para ESP32

```bash
arduino-cli config init
arduino-cli core update-index
arduino-cli core install esp32:esp32
```

---

## 🔥 Flashear el firmware (sin Arduino IDE)

Desde el directorio `neck/`, ejecuta el script de flasheo:

### Pasos:

1. **Mantén pulsado el botón BOOT** en tu ESP32-S3.
2. **Conecta el cable USB OTG** al PC.
3. Ejecuta:

```bash
python3 flash_firmware.py
```

---

## 📎 Reglas udev para /dev/esp32

Puedes configurar una regla `udev` para que tu ESP32-S3 aparezca siempre como `/dev/esp32`.

### Instalación automática:

```bash
sudo bash install_udev_rule.sh
```

### Lo que hace:

* Crea una regla en `/etc/udev/rules.d/99-esp32.rules`
* Asume `idVendor=303a` e `idProduct=1001`, típico de ESP32-S3 por USB CDC
* Al reconectar la placa, aparecerá en `/dev/esp32`

Si tu dispositivo usa otros valores, puedes obtener los correctos con:

```bash
udevadm info -a -n /dev/ttyACM0
```

---

## 📁 Estructura del proyecto

```
neck/
├── epj-neck/
│   └── epj-neck.ino             # Firmware principal
├── flash_firmware.py           # Script de flasheo automático
├── install_udev_rule.sh        # Script para instalar regla udev
├── keyboard_control.py         # Control manual desde teclado
├── neck_config.yaml            # Configuración de geometría y rangos
├── neck_control.py             # API de control en Python
└── readme.md                   # Este archivo
```

---

## 🧠 Notas

* Usa servos de rango fijo (0–180°). No servos de rotación continua.
* Este módulo es parte del ecosistema **HeWo Hardware**.
