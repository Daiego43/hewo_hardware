import pygame
import time
import math
import random
from neck_control import NeckControl
from enhanced_control import ServoFineController

MOVE_STEP = 10

# === INICIALIZACIÓN ===
neck = NeckControl()
ctl = ServoFineController(neck, move_step=MOVE_STEP)

# Ángulos iniciales
angles = [90, 90, 90]

# Colores
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Función de easing (número áureo)
def ease_in_out_phi(x: float) -> float:
    """Easing basado en el número áureo φ≈1.618."""
    phi = 1.618033988749895
    return 0.5 * (2 * x) ** phi if x < 0.5 else 1 - 0.5 * (2 * (1 - x)) ** phi

def teleop():
    pygame.init()

    # Configuración de la ventana
    screen = pygame.display.set_mode((900, 300))
    pygame.display.set_caption("Teleop Control - Ajuste de Ángulos")

    # Configuración de Pygame
    clock = pygame.time.Clock()
    running_harmonic = False  # Variable para alternar el recorrido armónico
    harmonic_goal = [90, 90, 90]  # Objetivo para el recorrido armónico

    font = pygame.font.SysFont("Arial", 24)

    # Ángulos iniciales
    global angles
    angles = [90, 90, 90]

    t_start = time.time()
    running = True

    while running:
        screen.fill((0, 0, 0))  # Limpia la pantalla

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Obtención de las teclas
        move_step = 5
        keys = pygame.key.get_pressed()

        # Controles para mover los servos
        if keys[pygame.K_q]:  # Mover servo 1 hacia arriba
            angles[0] += move_step
        if keys[pygame.K_a]:  # Mover servo 1 hacia abajo
            angles[0] -= move_step
        if keys[pygame.K_w]:  # Mover servo 2 hacia arriba
            angles[1] += move_step
        if keys[pygame.K_s]:  # Mover servo 2 hacia abajo
            angles[1] -= move_step
        if keys[pygame.K_e]:  # Mover servo 3 hacia arriba
            angles[2] += move_step
        if keys[pygame.K_d]:  # Mover servo 3 hacia abajo
            angles[2] -= move_step

        # Limitar el rango de los ángulos de los servos (0-180 grados)
        angles = [max(0, min(180, angle)) for angle in angles]

        # Actualizar los servos con la nueva configuración
        ctl.move_enhanced(angles, func=ease_in_out_phi, steps=1, blocking=False, move_step=move_step, freq=1)

        # Mostrar los valores de los ángulos y las instrucciones
        text1 = font.render(f"Servo 1: {angles[0]}°", True, WHITE)
        screen.blit(text1, (200, 50))
        text2 = font.render(f"Servo 2: {angles[1]}°", True, WHITE)
        screen.blit(text2, (200, 100))
        text3 = font.render(f"Servo 3: {angles[2]}°", True, WHITE)
        screen.blit(text3, (200, 150))

        instructions = font.render(
            "q: Servo1 ↑, w: Servo1 ↓ | e: Servo2 ↑, a: Servo2 ↓ | s: Servo3 ↑, d: Servo3 ↓ ",
            True, WHITE
        )
        screen.blit(instructions, (50, 200))

        # Actualizar la pantalla
        pygame.display.update()

        # Controlar la velocidad del bucle
        clock.tick(60)

    ctl.go_home()  # Regresar al home al finalizar
    pygame.quit()


if __name__ == "__main__":
    teleop()
