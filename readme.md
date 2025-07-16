# Espherical Parallel Joint
We are programming an spherical parallel joint or Stewart platform.
In our case we are using an external design from (TODO: Poner fuente del 3D Design)
We are using modified microservos sg90 that rotate continuously.

The intention of this repository is explore this kind of mechanism and develop my design in the future with other hardware
decisions and adaptations.

## The hardware

## How to use
### 0. (Optional) udev rule for esp32
In ubuntu esp32 or esp32-s3 can be found in `/dev/ttyUSB0` or `/dev/ttyACM0` .
Run this script to link the one connected to `/dev/esp32`
```bash
bash install_udev_rule.sh
```

### 1. Checkout the settings
Open `neck_config.yaml` and modifiy as you need. Example of a my servo config:
```yaml
# Specific servo configurations
servo_settings:
  1:  # DC servo motor. (Modified sg 90)
    type: continuous_rotation
    gpio: 23
    degrees_per_second: 600
    calibration_factor: 1.2  # For this servo
    min_move_threshold: 0.5  # Min move
    deadzone: 2              # Zona muerta PWM
    # PWM Signal configuration for this servo
    pwm_config:
      stop: 95
      max_cw: 140
      max_ccw: 50
    safety_limits:
      max_rotation_time_ms: 5000
```

2. Generate your .ino
```bash
python ino_generator.py 
```
3. Flash your firmware
```bash
python flash_firmware,py
```
4. Test the connection
```bash
python epj_neck.py
```