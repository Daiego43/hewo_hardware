import pygame
import serial
import yaml

# ----------- CLASES -------------
class Servo:
    def __init__(self, home_position=0, limits=(0, 180)):
        self.angle = home_position
        self.limits = limits

    def set_angle(self, angle):
        self.angle = max(self.limits['min'], min(self.limits['max'], angle))

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

    def send_command(self, timeout=0):
        command = 'S {} {} {}'.format(
            self.servo_1_angle.get_angle(),
            self.servo_2_angle.get_angle(),
            self.servo_3_angle.get_angle()
        )
        try:
            with serial.Serial(self.port, self.baudrate, timeout=timeout) as ser:
                ser.write((command + "\n").encode())
                print(f"Sent: {command}")
                return ser.readline().decode().strip()
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            return None

    def move(self, delta1=0, delta2=0, delta3=0):
        # Calcular nuevos ángulos
        new1 = self.servo_1_angle.get_angle() + delta1
        new2 = self.servo_2_angle.get_angle() + delta2
        new3 = self.servo_3_angle.get_angle() + delta3

        # Verificar diferencia máxima
        angles = [new1, new2, new3]
        if max(angles) - min(angles) > 60:
            print("Movimiento cancelado: diferencia entre servos mayor a 60°")
            return None

        # Aplicar cambios
        self.servo_1_angle.set_angle(new1)
        self.servo_2_angle.set_angle(new2)
        self.servo_3_angle.set_angle(new3)
        return self.send_command(timeout=0)

# ----------- MAIN -------------
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((600, 200))
    pygame.display.set_caption("Neck Control")
    font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    neck = NeckControl()
    keys_held = set()
    step = 5
    keymap = {
        pygame.K_q: (0, -step), pygame.K_w: (0, step),
        pygame.K_a: (1, -step), pygame.K_s: (1, step),
        pygame.K_z: (2, -step), pygame.K_x: (2, step),
    }

    running = True
    while running:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys_held.add(event.key)
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.KEYUP:
                keys_held.discard(event.key)

        deltas = [0, 0, 0]
        for key in keys_held:
            if key in keymap:
                idx, delta = keymap[key]
                deltas[idx] += delta

        if any(d != 0 for d in deltas):
            neck.move(*deltas)

        angles = [
            neck.servo_1_angle.get_angle(),
            neck.servo_2_angle.get_angle(),
            neck.servo_3_angle.get_angle()
        ]
        for i, val in enumerate(angles):
            txt = font.render(f"Servo {i+1}: {val}", True, (255, 255, 255))
            screen.blit(txt, (50, 40 * i + 20))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
