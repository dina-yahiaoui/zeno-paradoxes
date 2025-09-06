import sys
from pathlib import Path
import pygame as pg

THIS = Path(__file__).resolve()
SRC_DIR = THIS.parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ---------- Config ----------
DISTANCE_M = 10.0     # distance de trajet en mètres (pour les graduations & logs)
WIDTH, HEIGHT = 1000, 500
MARGIN_LEFT, MARGIN_RIGHT = 60, 40
TRACK_Y = HEIGHT // 2

BG    = (25, 28, 35)
GREY  = (90, 100, 115)
WHITE = (240, 240, 240)

# ---------- Sprites ----------
ASSETS_DIR = THIS.parents[2] / "assets"
ARROW_IMG  = ASSETS_DIR / "arrow.png"
CIBLE_IMG  = ASSETS_DIR / "cible.png"

def _load_sprite(path: Path, size=None):
    try:
        img = pg.image.load(str(path)).convert_alpha()
        if size:
            img = pg.transform.smoothscale(img, size)
        return img, True
    except Exception as e:
        print(f"[WARN] sprite introuvable: {path} -> {e}", flush=True)
        return None, False


class FlecheScene:
    """
    Paradoxe de la Flèche
    - Pygame: la flèche avanze vers la cible (arrow.png -> cible.png)
    - Terminal: logs réguliers t, x (m) et reste (m)
    - R: reset | ESC: menu
    """
    def __init__(self, screen, distance_px=800, speed_px=220):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.start_x = MARGIN_LEFT
        self.finish_x = self.start_x + distance_px
        self.y = TRACK_Y

        # cinématique
        self.speed_px = speed_px            # px/s (constante)
        self.pos_x = float(self.start_x)    # position en px depuis la gauche
        self.sim_time = 0.0

        # conversion px <-> m (pour logs & graduations)
        self.distance_px = distance_px
        self.m_per_px = DISTANCE_M / float(distance_px)

        # fonts & sprites
        self.font = pg.font.SysFont("consolas", 18)
        self.arrow_img, self.arrow_ok = _load_sprite(ARROW_IMG, (56, 56))
        self.cible_img, self.cible_ok = _load_sprite(CIBLE_IMG, (44, 44))

        # "fantômes" = instants figés (toutes les 0.5s)
        self.ghost_keys = set()
        self.ghost_positions = []  # [(tick_key, x_px)]

        # ---------- LOGGER TERMINAL ----------
        self.LOG_EVERY  = 0.1  # s simulées
        self.next_log_t = 0.0
        print("\n[FLÈCHE]   t (s) | x (m)       | reste (m)", flush=True)
        print("[FLÈCHE] ---------+-------------+-----------", flush=True)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_r:
            # reset animation
            self.pos_x = float(self.start_x)
            self.sim_time = 0.0
            self.ghost_keys.clear()
            self.ghost_positions.clear()
            self.next_log_t = 0.0
            print("\n[FLÈCHE] --- RESET ---", flush=True)
            print("[FLÈCHE]   t (s) | x (m)       | reste (m)", flush=True)
            print("[FLÈCHE] ---------+-------------+-----------", flush=True)

    def update(self, dt):
        # avancer la simulation
        if self.pos_x < self.finish_x:
            self.sim_time += dt
            self.pos_x = min(self.finish_x, self.pos_x + self.speed_px * dt)

            # logs chaque 0.1 s simulée
            while self.next_log_t <= self.sim_time:
                x_m     = max(0.0, (self.pos_x - self.start_x) * self.m_per_px)
                reste_m = max(0.0, (self.finish_x - self.pos_x) * self.m_per_px)
                print(f"[FLÈCHE] {self.next_log_t:7.2f} | {x_m:11.6f} | {reste_m:9.6f}", flush=True)
                self.next_log_t += self.LOG_EVERY

            # mémoriser des "instants figés" toutes les ~0.5 s
            key = int(pg.time.get_ticks() / 500)
            if key not in self.ghost_keys:
                self.ghost_keys.add(key)
                self.ghost_positions.append((key, self.pos_x))

    def draw(self):
        surf = self.screen
        surf.fill(BG)

        # piste + graduations 1 m
        pg.draw.line(surf, GREY, (MARGIN_LEFT, self.y), (self.W - MARGIN_RIGHT, self.y), 3)
        for m in range(0, int(DISTANCE_M) + 1):
            xg = int(self.start_x + m * (self.distance_px / DISTANCE_M))
            pg.draw.line(surf, GREY, (xg, self.y - 8), (xg, self.y + 8), 1)
            surf.blit(self.font.render(f"{m} m", True, GREY), (xg - 10, self.y + 12))

        # cible
        if self.cible_ok:
            rect = self.cible_img.get_rect(midbottom=(self.finish_x, self.y + 2))
            surf.blit(self.cible_img, rect)
        else:
            pg.draw.line(surf, (200, 30, 30), (self.finish_x, self.y - 50), (self.finish_x, self.y + 50), 3)

        # flèche actuelle
        if self.arrow_ok:
            a_rect = self.arrow_img.get_rect(midbottom=(int(self.pos_x), self.y + 2))
            surf.blit(self.arrow_img, a_rect)
        else:
            pg.draw.circle(surf, (200, 30, 30), (int(self.pos_x), self.y), 12)

        # fantômes
        if self.arrow_ok:
            ghost = self.arrow_img.copy(); ghost.set_alpha(110)
            for _, x in self.ghost_positions:
                grect = ghost.get_rect(midbottom=(int(x), self.y + 2))
                surf.blit(ghost, grect)
        else:
            for _, x in self.ghost_positions:
                s = pg.Surface((16, 16), pg.SRCALPHA)
                pg.draw.circle(s, (100, 180, 220, 140), (8, 8), 8)
                surf.blit(s, (int(x) - 8, self.y - 8))

        # textes
        title = self.font.render("Paradoxe de la flèche", True, WHITE)
        surf.blit(title, (self.W//2 - title.get_width()//2, 20))
        info = self.font.render("Reset: R  |  ESC: menu", True, WHITE)
        surf.blit(info, (20, self.H - 28))

