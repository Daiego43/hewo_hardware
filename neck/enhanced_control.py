"""
ServoFineController: control fino de 3 servos para el cuello.

Ejecuta como script para demo rápida:
    python servo_fine_controller.py

Ahora registra también los *goals* y los dibuja junto a la trayectoria real.
"""

from __future__ import annotations

import csv
import math
import time
from typing import Callable, Sequence, List

import matplotlib.pyplot as plt
from neck_control import NeckControl


class ServoFineController:
    """Control fino de 3 servos con registro y gráfica."""

    def __init__(
        self,
        neck: NeckControl,
        home_angles: Sequence[int] = (90, 90, 90),
        move_step: int = 10,
    ) -> None:
        self.neck = neck
        self.move_step = move_step
        self._current_angles: List[int] = list(home_angles)
        # [t, s1, s2, s3, g1, g2, g3]
        self._log: List[list[float | int]] = []
        # Lleva al home físico y sincroniza estado interno
        try:
            self.neck.go_home()
        except AttributeError:
            self.neck.move(*home_angles, timeout=0, move_step=self.move_step)
        self._current_angles = list(home_angles)

    # ------------------------------------------------------------------
    # Utilidades privadas
    # ------------------------------------------------------------------
    @property
    def current(self) -> List[int]:
        return self._current_angles.copy()

    @staticmethod
    def _ease_cos(x: float) -> float:
        return 0.5 - 0.5 * math.cos(math.pi * x)

    # ------------------------------------------------------------------
    # Movimiento principal
    # ------------------------------------------------------------------
    def move_enhanced(
        self,
        goal: Sequence[int],
        *,
        func: Callable[[float], float] | None = math.cos,
        freq: float = 1.0,
        steps: int = 60,
        move_step: int = 10,
        blocking: bool = True,
        dt: float = 0.02,
    ) -> None:
        """Mueve suavemente los servos hasta *goal* y registra trayectoria.
        """
        self.move_step = move_step

        if len(goal) != 3:
            raise ValueError("goal debe tener 3 ángulos (uno por servo)")

        if func is None:
            func = self._ease_cos

        start = self._current_angles.copy()

        for i in range(steps + 1):
            phase = (i / steps) * freq
            prog = max(0.0, min(1.0, func(phase)))
            angles = [round(s + (g - s) * prog) for s, g in zip(start, goal)]

            self.neck.move(*angles, timeout=0, move_step=self.move_step)
            self._current_angles = angles
            self._log.append([time.time(), *angles, *goal])

            if blocking and i < steps:
                time.sleep(dt)

    # ------------------------------------------------------------------
    # Registro y gráficas
    # ------------------------------------------------------------------
    def plot_and_save(
        self,
        csv_path: str = "servo_log.csv",
        fig_path: str | None = None,
        show: bool = True,
    ) -> None:
        """Guarda CSV y dibuja trayectoria real + goals."""
        if not self._log:
            print("[ServoFineController] No hay datos registrados.")
            return

        # Guarda CSV
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "servo1", "servo2", "servo3", "goal1", "goal2", "goal3"])
            writer.writerows(self._log)
        print(f"[ServoFineController] CSV guardado en {csv_path}")

        # Extrae datos
        t0 = self._log[0][0]
        times = [row[0] - t0 for row in self._log]
        s1, s2, s3 = zip(*[(row[1], row[2], row[3]) for row in self._log])
        g1, g2, g3 = zip(*[(row[4], row[5], row[6]) for row in self._log])

        plt.figure()
        plt.plot(times, s1, label="Servo 1")
        plt.plot(times, s2, label="Servo 2")
        plt.plot(times, s3, label="Servo 3")
        plt.plot(times, g1, "--", label="Goal 1")
        plt.plot(times, g2, "--", label="Goal 2")
        plt.plot(times, g3, "--", label="Goal 3")
        plt.xlabel("Tiempo (s)")
        plt.ylabel("Ángulo (°)")
        plt.title("Trayectoria de servos vs Goal")
        plt.legend()
        plt.tight_layout()

        if fig_path:
            plt.savefig(fig_path)
            print(f"[ServoFineController] Figura guardada en {fig_path}")

        if show:
            plt.show()
        else:
            plt.close()

    def reset_log(self) -> None:
        self._log.clear()

    # ------------------------------------------------------------------
    # Atajos
    # ------------------------------------------------------------------
    def go_home(self) -> None:
        self.move_enhanced(self._current_angles, steps=1)
        try:
            self.neck.go_home()
            self._current_angles = [90, 90, 90]
        except AttributeError:
            pass


# =====================================================================
# Easing extra (para pruebas)
# =====================================================================

def ease_in_out_back(x: float) -> float:
    c1, c2 = 1.70158, 1.70158 * 1.525
    return ((2*x)**2 * ((c2+1)*2*x - c2))/2 if x < 0.5 else (((2*x-2)**2)*((c2+1)*(2*x-2)+c2)+2)/2

def ease_in_elastic(x: float) -> float:
    if x in (0, 1):
        return x
    return -math.pow(2, 10*x - 10) * math.sin((x*10 - 10.75)*(2*math.pi/3))

def bounce_out(x: float) -> float:
    n1, d1 = 7.5625, 2.75
    if x < 1/d1:
        return n1*x*x
    if x < 2/d1:
        x -= 1.5/d1
        return n1*x*x + 0.75
    if x < 2.5/d1:
        x -= 2.25/d1
        return n1*x*x + 0.9375
    x -= 2.625/d1
    return n1*x*x + 0.984375

def bounce_in_out(x: float) -> float:
    return (1 - bounce_out(1 - 2*x))/2 if x < 0.5 else (1 + bounce_out(2*x - 1))/2

bounce_in = lambda x: 1 - bounce_out(1 - x)

def ease_in_out_phi(x: float) -> float:
    """Easing basado en el número áureo φ≈1.618."""
    phi = 1.618033988749895
    return 0.5 * (2*x) ** phi if x < 0.5 else 1 - 0.5 * (2*(1 - x)) ** phi

# =====================================================================
# Bloque de prueba / demo
# =====================================================================

if __name__ == "__main__":
    import random

    neck = NeckControl()
    ctl = ServoFineController(neck, move_step=2)

    try:
        for _ in range(5):
            goal = [random.randint(0, 180) for _ in range(3)]
            print("GOAL →", goal)
            ctl.move_enhanced(goal,
                              freq=1.0,
                              steps=20,
                              func=ease_in_out_phi,
                              move_step=1,
                              blocking=True)
    except KeyboardInterrupt:
        pass
    finally:
        ctl.go_home()
        ctl.plot_and_save(csv_path="servo_log.csv", fig_path="servo_plot.png")
