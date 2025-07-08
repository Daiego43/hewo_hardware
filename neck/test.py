import time
import math
from neck_control import NeckControl  # Asegúrate de que el script esté en el mismo directorio o PYTHONPATH

neck = NeckControl()
def sinusoidal_motion(duration=10, freq=0.5, servo_index=1, amplitude=85, base=95):
    """
    Mueve un servo con velocidad sinusoidal.

    :param duration: Duración total en segundos
    :param freq: Frecuencia de la onda (Hz)
    :param servo_index: Servo a controlar (1, 2 o 3)
    :param amplitude: Amplitud máxima de desviación desde el valor base (PWM)
    :param base: Valor base de velocidad (por defecto 95 = parado)
    """
    start = time.time()

    print(f"🎢 Sinusoidal motion on servo {servo_index} for {duration}s")
    while time.time() - start < duration:
        t = time.time() - start
        velocity = int(90 + 90 * math.sin(2 * math.pi * freq * t))

        # Garantizar rango válido
        velocity = max(0, min(180, velocity))

        v1 = v2 = v3 = base
        if servo_index == 1:
            v1 = velocity
        elif servo_index == 2:
            v2 = velocity
        elif servo_index == 3:
            v3 = velocity

        neck.set_velocity(v1, v2, v3)
        time.sleep(0.02)  # ~50Hz

    print("🛑 Stopping...")
    neck.go_home()
    neck.go_home()
    neck.go_home()
    neck.go_home()
    neck.go_home()


if __name__ == '__main__':

    sinusoidal_motion(duration=2, freq=0.2, servo_index=1, amplitude=10)
    sinusoidal_motion(duration=2, freq=0.2, servo_index=2, amplitude=10)
    sinusoidal_motion(duration=2, freq=0.2, servo_index=3, amplitude=10)
    neck.set_velocity(0,0,0)
    time.sleep(1)
    neck.set_velocity(180,180,180)
    time.sleep(1)
    neck.go_home()
