import sys
from pathlib import Path

THIS_FILE = Path(__file__).resolve()
SRC_DIR = THIS_FILE.parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fleche.fleche_vol import simulate

import pygame

V = 5.0
DT = 0.2
T_MAX = 10.0
TIME_SCALE = 1.0
LOG_EVERY = 0.5

WIDTH, HEIGHT = 800, 300
MARGIN_LEFT, MARGIN_RIGHT = 60, 40
TRACK_Y = HEIGHT // 2
SCALE = 50

BG    = (25, 28, 35)
GREY  = (90, 100, 115)
WHITE = (240, 240, 240)
RED   = (200, 80, 80)
BLACK = (0, 0, 0)


def build_trajectory():
    results = simulate(v=V, t_max=T_MAX, dt=DT)
    return results


def interpolate_at(target_t, results, start_idx=0):
    n = len(results)
    i = start_idx
    while i + 1 < n and results[i + 1][0] <= target_t:
        i += 1
    t_i, x_i = results[i]
    if i + 1 < n:
        t_j, x_j = results[i + 1]
        if t_j > t_i:
            alpha = (target_t - t_i) / (t_j - t_i)
        else:
            alpha = 0.0
        x_val = x_i + alpha * (x_j - x_i)
        return target_t, x_val, i
    else:
        return results[-1][0], results[-1][1], i


def main():
    results = build_trajectory()
    if len(results) < 2:
        print("[ERROR] Trajectoire trop courte. Vérifie DT et T_MAX.")
        return

    print("t (s) | Flèche (m)")
    print("-" * 20)
    next_log_t = 0.0
    log_idx = 0

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Paradoxe de la flèche — Terminal + Pygame")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    sim_time = 0.0
    anim_idx = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                results = build_trajectory()
                sim_time = 0.0
                anim_idx = 0
                next_log_t = 0.0
                log_idx = 0
                print("\n--- RESET ---")
                print("t (s) | Flèche (m)")
                print("-" * 20)

        dt_real = clock.get_time() / 1000.0
        sim_time += dt_real * TIME_SCALE
        if sim_time > results[-1][0]:
            sim_time = results[-1][0]

        while next_log_t <= sim_time and next_log_t <= results[-1][0]:
            t_log, x_log, log_idx = interpolate_at(next_log_t, results, start_idx=log_idx)
            print(f"{t_log:5.1f} | {x_log:9.2f}")
            next_log_t += LOG_EVERY

        t, x, anim_idx = interpolate_at(sim_time, results, start_idx=anim_idx)

        screen.fill(BG)
        pygame.draw.line(screen, GREY, (MARGIN_LEFT, TRACK_Y), (WIDTH - MARGIN_RIGHT, TRACK_Y), 3)
        x_px = min(MARGIN_LEFT + int(x * SCALE), WIDTH - MARGIN_RIGHT)
        pygame.draw.rect(screen, BLACK, (x_px, TRACK_Y - 5, 30, 10))
        pygame.draw.circle(screen, RED, (WIDTH - MARGIN_RIGHT, TRACK_Y), 15)
        info = f"t={t:5.2f}s | x={x:6.2f} m | v={V}"
        screen.blit(font.render(info, True, WHITE), (20, 12))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()