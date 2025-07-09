import time
import math
from neck_control import NeckServoController  # Asegúrate de que el nombre sea correcto

def sinusoidal_motion(ctrl, servo_index, duration=10, freq=0.5, amplitude=85, base=95):
    """
    Mueve un servo con velocidad PWM sinusoidal.

    :param ctrl: instancia de NeckServoController
    :param servo_index: Índice del servo (0, 1, 2)
    :param duration: Duración total en segundos
    :param freq: Frecuencia de la onda (Hz)
    :param amplitude: Máxima desviación desde el valor base
    :param base: PWM base (normalmente 95 = stop)
    """
    print(f"🎢 Sinusoidal motion on servo {servo_index} for {duration}s")
    start = time.time()

    while time.time() - start < duration:
        t = time.time() - start
        pwm = int(base + amplitude * math.sin(2 * math.pi * freq * t))

        # Asegura que esté dentro del rango válido
        pwm = max(0, min(180, pwm))

        # Aplica solo al servo indicado
        ctrl.set_pwm_index(servo_index, pwm)
        time.sleep(0.02)  # 50Hz

def stepped_motion(ctrl, servo_index, target_angle, direction='clock'):
    """
    Mueve un servo a una posición específica con un paso.

    :param ctrl: instancia de NeckServoController
    :param servo_index: Índice del servo (0, 1, 2)
    :param target_angle: Ángulo objetivo en grados
    :param direction: Dirección del movimiento ('clock' o 'antic')
    """
    print(f"🚀 Stepped motion on servo {servo_index} to {target_angle}° in direction {direction}")
    ctrl.servo_list[servo_index].step_to(target_angle, direction)


if __name__ == '__main__':
    ctrl = NeckServoController("neck_config.yaml")
    ctrl.stop_all()
    time.sleep(1)
    try:
        # for i in [0, 45, 90, 135, 180, 225,270, 315, 360]:
        #     stepped_motion(ctrl, servo_index=0, target_angle=i, direction='clock')
        #     time.sleep(0.2)
        # for i in [0, 45, 90, 135, 180, 225,270, 315, 360]:
        #     stepped_motion(ctrl, servo_index=0, target_angle=i, direction='antic')
        #     time.sleep(0.2)
        sinusoidal_motion(ctrl, servo_index=0, duration=5, freq=0.2, amplitude=85)
        print("🛑 Stopping...")
        ctrl.stop_all()
    finally:
        ctrl.stop_all()
        ctrl.close()
