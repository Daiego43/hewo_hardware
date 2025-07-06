import serial
import yaml



class Servo:
    def __init__(self, home_position=0, limits=(0, 180)):
        self.angle = home_position
        self.limits = limits

    def set_angle(self, angle):
        if angle < self.limits['min'] or angle > self.limits['max']:
            print("Angle must be between 0 and 180 degrees.")
        self.angle = angle

    def get_angle(self):
        return self.angle

class NeckControl:
    def __init__(self):
        with open('epj-neck/board_settings.yaml', 'r') as f:
            settings = yaml.safe_load(f)
        self.port = settings['port']
        self.baudrate = settings['baudrate']

        with open('neck_config.yaml', 'r') as f:
            servo_settings = yaml.safe_load(f)
        self.servo_1_angle = Servo(servo_settings['servo_settings'][1]['home_position'], servo_settings['servo_settings'][1]['limits'])
        self.servo_2_angle = Servo(servo_settings['servo_settings'][2]['home_position'], servo_settings['servo_settings'][2]['limits'])
        self.servo_3_angle = Servo(servo_settings['servo_settings'][3]['home_position'], servo_settings['servo_settings'][3]['limits'])


    def send_command(self, timeout=1):
        command = 'S {} {} {}'.format(self.servo_1_angle.get_angle(), self.servo_2_angle.get_angle(), self.servo_3_angle.get_angle())
        with serial.Serial(self.port, self.baudrate, timeout=timeout) as ser:
            ser.write((command + "\n").encode())
            print(f"Sent: {command}")
            return ser.readline().decode().strip()

    def move(self, servo_1_angle=0, servo_2_angle=0, servo_3_angle=0, timeout=1):
        self.servo_1_angle.set_angle(servo_1_angle)
        self.servo_2_angle.set_angle(servo_2_angle)
        self.servo_3_angle.set_angle(servo_3_angle)
        return self.send_command(timeout)

if __name__ == '__main__':
    neck_control = NeckControl()
    for angle in [0, 30, 60, 90, 120, 150, 180, 0]:
        neck_control.move(angle, angle, angle, timeout=1)

