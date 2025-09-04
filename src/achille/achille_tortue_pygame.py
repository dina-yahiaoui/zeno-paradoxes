# src/achille/achille_tortue_pygame.py
import sys
from pathlib import Path

# --- Rendre importable: mettre src/ dans sys.path pour "from achille.achille_tortue import simulate"
THIS_FILE = Path(__file__).resolve()
SRC_DIR = THIS_FILE.parents[1]   # .../src
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from achille.achille_tortue import simulate  # <-- ALGORITHME réutilisé

import pygame

# -----------------------------
# Paramètres de simulation
# -----------------------------
V_ACHILLE = 5.0
V_TORTUE  = 2.0
LEAD      = 20.0
DT        = 0.05     # pas de simulation pour generate results
T_MAX     = 60.0
TIME_SCALE = 1.0     # 1.0=temps réel; 2.0=2x plus vite

# Logging terminal (fréquence d'impression)
LOG_EVERY = 0.1      # secondes simulées

# -----------------------------
# Affichage (Pygame)
# -----------------------------
WIDTH, HEIGHT = 1000, 260
MARGIN_LEFT, MARGIN_RIGHT = 60, 40
TRACK_Y = HEIGHT // 2
SCALE = 10

BG    = (25, 28, 35)
GREY  = (90, 100, 115)
BLUE  = (110, 160, 255)
GREEN = (100, 200, 120)
WHITE = (240, 240, 240)
YELL  = (240, 200, 80)

# Assets PNG
ASSETS_DIR = THIS_FILE.parents[2] / "assets"  # .../zeno-paradoxes/assets
ACHILLE_IMG_PATH = ASSETS_DIR / "achille.png"
TORTUE_IMG_PATH  = ASSETS_DIR / "tortue.png"

def load_sprite(path: Path, size=(48, 48)):
    try:
        img = pygame.image.load(str(path)).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img, True
    except Exception as e:
        print(f"[WARN] Sprite introuvable: {path} -> {e}")
        return None, False

def build_trajectory():
    """Appelle l'algo unique pour construire la trajectoire discrète (liste de (t, xA, xT))."""
    results, info = simulate(
        v_achille=V_ACHILLE,
        v_tortue=V_TORTUE,
        lead=LEAD,
        dt=DT,
        t_max=T_MAX,
    )
    return results, info

def interpolate_at(target_t, results, start_idx=0):
    """
    Renvoie (t, xA, xT, idx) pour l'instant target_t en interpolant linéairement
    entre results[idx] et results[idx+1]. start_idx permet d'éviter de repartir de 0 à chaque fois.
    """
    n = len(results)
    i = start_idx
    # avancer i jusqu'à ce que results[i].t <= target_t < results[i+1].t
    while i + 1 < n and results[i + 1][0] <= target_t:
        i += 1
    t_i, xa_i, xt_i = results[i]
    if i + 1 < n:
        t_j, xa_j, xt_j = results[i + 1]
        if t_j > t_i:
            alpha = (target_t - t_i) / (t_j - t_i)
        else:
            alpha = 0.0
        x_a = xa_i + alpha * (xa_j - xa_i)
        x_t = xt_i + alpha * (xt_j - xt_i)
        return target_t, x_a, x_t, i
    else:
        # target_t est en fin de trajectoire
        return results[-1][0], results[-1][1], results[-1][2], i

def main():
    # 1) Construire la trajectoire via l'ALGORITHME importé
    results, (caught_final, t_hit_final, x_hit_final) = build_trajectory()
    if len(results) < 2:
        print("[ERROR] Trajectoire trop courte. Vérifie DT et T_MAX.")
        return

    # 2) Préparer le logging terminal
    print("t (s) | Achille (m) | Tortue (m)")
    print("-" * 28)
    next_log_t = 0.0
    log_idx = 0  # index pour accélérer l'interpolation côté terminal

    # 3) Init Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Achille & la Tortue — (algo importé) Terminal + Pygame")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    achille_sprite, achille_ok = load_sprite(ACHILLE_IMG_PATH, (48, 48))
    tortue_sprite,  tortue_ok  = load_sprite(TORTUE_IMG_PATH,  (48, 48))

    # 4) État de l'animation
    sim_time = 0.0   # temps simulé affiché à l'écran
    anim_idx = 0     # index pour l'interpolation côté animation
    caught_runtime = False

    running = True
    while running:
        # a) Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Recalculer la trajectoire et réinitialiser
                results, (caught_final, t_hit_final, x_hit_final) = build_trajectory()
                sim_time = 0.0
                anim_idx = 0
                next_log_t = 0.0
                log_idx = 0
                caught_runtime = False
                print("\n--- RESET ---")
                print("t (s) | Achille (m) | Tortue (m)")
                print("-" * 28)

        # b) Avancer le temps simulé en fonction du temps réel
        dt_real = clock.get_time() / 1000.0
        sim_time += dt_real * TIME_SCALE
        if sim_time > results[-1][0]:
            sim_time = results[-1][0]

        # c) LOGGING TERMINAL à cadence régulière (selon le temps simulé)
        # Imprimer autant de lignes que nécessaire tant que sim_time a dépassé next_log_t
        while next_log_t <= sim_time and next_log_t <= results[-1][0]:
            t_log, xa_log, xt_log, log_idx = interpolate_at(next_log_t, results, start_idx=log_idx)
            print(f"{t_log:5.1f} | {xa_log:11.2f} | {xt_log:9.2f}")
            next_log_t += LOG_EVERY

        # d) Position pour l'ANIMATION (interpolation au temps sim_time)
        t, x_a, x_t, anim_idx = interpolate_at(sim_time, results, start_idx=anim_idx)

        if not caught_runtime and x_a >= x_t:
            caught_runtime = True

        # e) DESSIN
        screen.fill(BG)

        # piste
        pygame.draw.line(screen, GREY, (MARGIN_LEFT, TRACK_Y), (WIDTH - MARGIN_RIGHT, TRACK_Y), 3)

        # graduations
        max_m = int((WIDTH - MARGIN_LEFT - MARGIN_RIGHT) / SCALE)
        for m in range(0, max_m + 1, 10):
            xg = MARGIN_LEFT + m * SCALE
            pygame.draw.line(screen, GREY, (xg, TRACK_Y - 10), (xg, TRACK_Y + 10), 1)
            screen.blit(font.render(f"{m} m", True, GREY), (xg - 14, TRACK_Y + 14))

        # conversion mètres -> pixels
        x_a_px = min(MARGIN_LEFT + int(x_a * SCALE), WIDTH - MARGIN_RIGHT)
        x_t_px = min(MARGIN_LEFT + int(x_t * SCALE), WIDTH - MARGIN_RIGHT)

        # sprites (fallback ronds si absents)
        if achille_ok:
            screen.blit(achille_sprite, achille_sprite.get_rect(center=(x_a_px, TRACK_Y)))
        else:
            pygame.draw.circle(screen, BLUE, (x_a_px, TRACK_Y), 12)
        if tortue_ok:
            screen.blit(tortue_sprite, tortue_sprite.get_rect(center=(x_t_px, TRACK_Y)))
        else:
            pygame.draw.circle(screen, GREEN, (x_t_px, TRACK_Y), 12)

        # infos
        info = f"t={t:5.2f}s | xA={x_a:6.2f} m | xT={x_t:6.2f} m | vA={V_ACHILLE} | vT={V_TORTUE}"
        screen.blit(font.render(info, True, WHITE), (20, 12))

        if caught_runtime:
            screen.blit(font.render("✅ Rattrapée", True, YELL), (20, HEIGHT - 36))
            # On affiche aussi le t_hit exact uniquement à ce moment
            if caught_final:
                screen.blit(font.render(f"t_hit (algo) ≈ {t_hit_final:.2f}s @ x ≈ {x_hit_final:.2f} m",
                                True, WHITE), (20, HEIGHT - 18))


        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
