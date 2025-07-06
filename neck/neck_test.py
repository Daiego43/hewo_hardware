import math
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from neck_control import NeckControl

# === CONFIGURACIÓN GENERAL ===
OFFSET = 90
AMPLITUDE = 90
FREQ = 0.2
WINDOW = 10
FPS = 20
MOVE_STEP = 2

# === INICIALIZACIÓN ===
neck = NeckControl()
fig, ax = plt.subplots()
ax.set_xlim(0, WINDOW)
ax.set_ylim(OFFSET - AMPLITUDE - 10, OFFSET + AMPLITUDE + 10)
lines = [ax.plot([], [], label=f"Servo {i+1}")[0] for i in range(3)]
ax.legend()
xdata = []
ydata = [[], [], []]
t_start = time.time()

# === CÁLCULO DE ÁNGULOS INDIVIDUALES ===
def generate_angles(t):
    angles = []
    for cfg in servo_config:
        phase_t = t + cfg["dephase"]
        val = cfg["func"](2 * math.pi * FREQ * phase_t)
        angle = round(OFFSET + AMPLITUDE * val)
        angles.append(angle)
    return angles

# === ACTUALIZACIÓN DE ANIMACIÓN ===
def update(_):
    t = time.time() - t_start
    xdata.append(t)
    angles = generate_angles(t)
    neck.move(*angles, timeout=0, move_step=MOVE_STEP)

    for i in range(3):
        ydata[i].append(angles[i])
        lines[i].set_data(xdata, ydata[i])
    ax.set_xlim(max(0, t - WINDOW), t + 1)
    return lines

# === EJECUCIÓN ===


def main():
    neck.go_home()
    print("Neck initialized and moved to home position.")
    neck.go_home()
    try:
        ani = animation.FuncAnimation(fig, update, interval=1000 // FPS, blit=False)
        plt.show()
    except KeyboardInterrupt:
        print("Stopped by user.")
        neck.go_home()

if __name__ == '__main__':
    constant = lambda t: 0
    servo_config = [
        {"func": math.cos, "dephase": 0.0},
        {"func": math.cos, "dephase": 0.2},
        {"func": math.cos, "dephase": 0.4},
    ]
    print(servo_config)
    main()