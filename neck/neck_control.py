import serial
import yaml
import os


class Servo:
    def __init__(self, home_position=0, limits=None):
        self.angle = home_position
        self.home_position = home_position
        self.limits = limits or {'min': 0, 'max': 180}

    def set_angle(self, angle):
        if angle < self.limits['min'] or angle > self.limits['max']:
            print(f"Rejected: angle {angle}° out of range [{self.limits['min']}, {self.limits['max']}]")
            return
        self.angle = angle

    def get_angle(self):
        return self.angle

    def go_home(self):
        self.set_angle(self.home_position)
        print(f"Moved to home position: {self.home_position}°")


class NeckControl:
    def __init__(self, config_file='neck_config.yaml'):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
        with open(path, 'r') as f:
            settings = yaml.safe_load(f)

        board = settings['board_settings']
        self.port = board['port']
        self.baudrate = board.get('baudrate', 115200)

        servo_cfg = settings['servo_settings']
        self.servo_1_angle = Servo(servo_cfg[1]['home_position'], servo_cfg[1]['limits'])
        self.servo_2_angle = Servo(servo_cfg[2]['home_position'], servo_cfg[2]['limits'])
        self.servo_3_angle = Servo(servo_cfg[3]['home_position'], servo_cfg[3]['limits'])

        self.move_step = 1

    def send_command(self, timeout=1):
        command = 'D {} {} {} {}'.format(
            self.servo_1_angle.get_angle(),
            self.servo_2_angle.get_angle(),
            self.servo_3_angle.get_angle(),
            self.move_step
        )
        with serial.Serial(self.port, self.baudrate, timeout=timeout) as ser:
            ser.write((command + "\n").encode())
            print(f"Sent: {command}")
            response = ser.readline().decode().strip()
            print(f"Received: {response}")
            return response

    def move(self, servo_1_angle=0, servo_2_angle=0, servo_3_angle=0, move_step=1, timeout=1):
        self.servo_1_angle.set_angle(servo_1_angle)
        self.servo_2_angle.set_angle(servo_2_angle)
        self.servo_3_angle.set_angle(servo_3_angle)
        self.move_step = move_step
        return self.send_command(timeout)

    def go_home(self):
        self.servo_1_angle.go_home()
        self.servo_2_angle.go_home()
        self.servo_3_angle.go_home()
        return self.send_command()

if __name__ == '__main__':
    neck_control = NeckControl()
    for angle in [0, 30, 60, 90, 120, 150, 180]:
        neck_control.move(angle, angle, angle, timeout=1)

    neck_control.go_home()
