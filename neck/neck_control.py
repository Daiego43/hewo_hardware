import serial
import time
import yaml


class Servo:
    def __init__(self, init_vel, min_pwm, max_pwm, stop_vel, degrees_per_second=600, index=None, controller=None):
        self.stop_vel = stop_vel
        self.pwm = init_vel
        self.min_pwm = min_pwm
        self.max_pwm = max_pwm
        self.degrees_per_second = degrees_per_second
        self.position = 0.0  # posición estimada
        self.index = index  # índice en servo_list
        self.controller = controller  # instancia de NeckServoController

        print("Servo initialized with:")
        print(f"  Initial Velocity: {init_vel}, {type(init_vel)}")
        print(f"  Min PWM: {min_pwm}, {type(min_pwm)}")
        print(f"  Max PWM: {max_pwm}, {type(max_pwm)}")
        print(f"  Stop Velocity: {stop_vel}, {type(stop_vel)}")
        print(f"  Estimated position: {self.position}°")

    def set_pwm(self, value):
        self.pwm = max(self.min_pwm, min(self.max_pwm, value))

    def stop(self):
        self.set_pwm(self.stop_vel)

    def get_pwm(self):
        return self.pwm

    def get_position(self):
        return self.position

    def step_to(self, target_angle, direction):
        """
        Mueve el servo desde su posición estimada hacia `target_angle`,
        usando la dirección ('clock' o 'antic') y velocidad máxima.
        """
        if self.controller is None or self.index is None:
            raise RuntimeError("No controller or index linked to this servo.")

        delta = abs(target_angle - self.position)
        if delta < 1:
            print("🎯 Ya está en posición.")
            return

        # PWM según dirección
        if direction == 'clock':
            pwm = self.min_pwm
        elif direction == 'antic':
            pwm = self.max_pwm
        else:
            raise ValueError("Dirección debe ser 'clock' o 'antic'")

        duration = delta / self.degrees_per_second
        print(f"🚀 Servo {self.index}: {self.position:.1f}° → {target_angle:.1f}° "
              f"en dirección {direction.upper()} ({duration:.2f}s, PWM={pwm})")

        self.set_pwm(pwm)
        self.controller.set_pwm_index(self.index, self.pwm)

        time.sleep(duration)

        self.stop()
        self.controller.set_pwm_index(self.index, self.pwm)
        self.position = target_angle



    # Stepper motor control

class NeckServoController:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        board = self.config['board_settings']
        self.port = board['port']
        self.baudrate = board.get('baudrate', 115200)
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        time.sleep(2)

        self.servo_settings = self.config['servo_settings']
        self.servo_list = []

        for idx, key in enumerate(sorted(self.servo_settings.keys())):
            settings = self.servo_settings[key]
            servo = Servo(
                init_vel=settings.get('init_vel', 95),
                min_pwm=settings.get('min_pwm', 0),
                max_pwm=settings.get('max_pwm', 180),
                stop_vel=settings.get('stop_vel', 95),
                degrees_per_second=settings.get('degrees_per_second', 600),
                index=idx,
                controller=self
            )
            self.servo_list.append(servo)

        print("🌀 ServoController ready.")

    def set_pwm(self, pwm_list):
        for i, val in enumerate(pwm_list):
            self.servo_list[i].set_pwm(val)
        cmd = "V " + " ".join(f"{s.get_pwm():.1f}" for s in self.servo_list) + "\n"
        self.ser.write(cmd.encode('utf-8'))
        print(f"➡️ Sent: {cmd.strip()}")

    def set_pwm_index(self, index, pwm_value):
        self.servo_list[index].set_pwm(pwm_value)
        cmd = "V " + " ".join(f"{s.get_pwm():.1f}" for s in self.servo_list) + "\n"
        self.ser.write(cmd.encode('utf-8'))
        print(f"➡️ Sent: {cmd.strip()}")

    def stop_all(self):
        for s in self.servo_list:
            s.stop()
        self.set_pwm([s.get_pwm() for s in self.servo_list])
        self.set_pwm([s.get_pwm() for s in self.servo_list])

    def close(self):
        self.ser.close()




# Ejemplo de uso
if __name__ == "__main__":
    ctrl = NeckServoController("neck_config.yaml")
    angle = 0
    try:
        s0 = ctrl.servo_list[0]
        while True:
            input(f"🔁 Enter para ir a {angle}° (CLOCKWISE)")
            s0.step_to(angle, direction="clock")
            input("🔁 Enter para ir a 90° (ANTICLOCKWISE)")
            s0.step_to(90, direction="antic")
    finally:
        ctrl.stop_all()
        ctrl.close()


