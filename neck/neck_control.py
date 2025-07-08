import serial
import yaml
import os


class Servo:
    def __init__(self, home_position=95, limits=None):
        self.angle = home_position
        self.home_position = home_position
        self.limits = limits or {'min': 0, 'max': 180}

    def set_angle(self, angle):
        if angle < self.limits['min'] or angle > self.limits['max']:
            print(f"⚠️ Rejected: angle {angle}° out of range [{self.limits['min']}, {self.limits['max']}]")
            return
        self.angle = angle

    def get_angle(self):
        return self.angle

    def go_home(self):
        self.set_angle(self.home_position)
        print(f"🏠 Moved to home position: {self.home_position}°")


class NeckControl:
    def __init__(self, config_file='neck_config.yaml'):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
        with open(path, 'r') as f:
            settings = yaml.safe_load(f)

        board = settings['board_settings']
        self.port = board['port']
        self.baudrate = board.get('baudrate', 115200)

        servo_cfg = settings['servo_settings']
        self.servo_1 = Servo(servo_cfg[1]['home_position'], servo_cfg[1]['limits'])
        self.servo_2 = Servo(servo_cfg[2]['home_position'], servo_cfg[2]['limits'])
        self.servo_3 = Servo(servo_cfg[3]['home_position'], servo_cfg[3]['limits'])

    def send(self, command, timeout=2):
        try:
            with serial.Serial(self.port, self.baudrate, timeout=timeout) as ser:
                ser.reset_input_buffer()
                ser.write((command + "\n").encode())
                print(f"🛰️ Sent: {command}")
                response = ser.readline().decode().strip()
                print(f"📬 Received: {response}")
                return response
        except serial.SerialException as e:
            print(f"❌ Serial error: {e}")
            return None

    def set_velocity(self, v1=95, v2=95, v3=95):
        # v1, v2, v3 deben ser enteros entre 0 y 180
        v1 = max(0, min(180, int(v1)))
        v2 = max(0, min(180, int(v2)))
        v3 = max(0, min(180, int(v3)))
        cmd = f"V {v1} {v2} {v3}"
        return self.send(cmd)

    def go_home(self):
        return self.set_velocity(
            self.servo_1.home_position,
            self.servo_2.home_position,
            self.servo_3.home_position
        )


if __name__ == '__main__':
    neck = NeckControl()
    import time
    print("📦 TEST SEQUENCE: set speed, stop, home")

    while True:
        input("🛑 ENTER to set custom velocity...")
        neck.set_velocity(180, 180, 180)  # Ejemplo: cada motor diferente
        input("🛑 ENTER to set custom velocity...")
        neck.set_velocity(0, 0, 0)  # Ejemplo: cada motor diferente
        input("✋ ENTER to stop all...")
        neck.go_home()
