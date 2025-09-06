import sys
from pathlib import Path
import pygame as pg

THIS = Path(__file__).resolve()
SRC_DIR = THIS.parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# ---------- Config ----------
DISTANCE_M = 8.0   # distance pierre-arbre en mètres
WIDTH, HEIGHT = 1000, 500
MARGIN_LEFT, MARGIN_RIGHT = 60, 40
TRACK_Y = HEIGHT // 2

BG    = (25, 28, 35)
GREY  = (90, 100, 115)
WHITE = (240, 240, 240)

# ---------- Sprites ----------
ASSETS_DIR = THIS.parents[2] / "assets"
PIERRE_IMG = ASSETS_DIR / "pierre.png"
ARBRE_IMG  = ASSETS_DIR / "arbre.png"

def _load_sprite(path: Path, size=None):
    try:
        img = pg.image.load(str(path)).convert_alpha()
        if size:
            img = pg.transform.smoothscale(img, size)
        return img, True
    except Exception as e:
        print(f"[WARN] sprite introuvable: {path} -> {e}", flush=True)
        return None, False


class DichotomieScene:
    def __init__(self, screen, distance_px=800, speed_px=200, epsilon=1):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.start_x = MARGIN_LEFT
        self.finish_x = self.start_x + distance_px
        self.y = TRACK_Y

        self.speed = speed_px
        self.epsilon = epsilon

        self.pos_x = float(self.start_x)
        self.target_x = (self.pos_x + self.finish_x) // 2

        self.font = pg.font.SysFont("consolas", 18)
        self.steps = 0
        self.done = False

        # sprites
        self.pierre_img, self.pierre_ok = _load_sprite(PIERRE_IMG, (40, 40))
        self.arbre_img,  self.arbre_ok  = _load_sprite(ARBRE_IMG, (64, 64))

        # conversion px -> mètres
        self.distance_px = distance_px
        self.m_per_px = DISTANCE_M / float(distance_px)

        # ---------- LOGGER TERMINAL ----------
        print("\n[DICHOTOMIE] Étape |  +Δ (m)   |  parcouru (m)  |  reste (m)", flush=True)
        print("[DICHOTOMIE] ----- | ---------- | -------------- | ----------", flush=True)

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_r:
            self.pos_x = float(self.start_x)
            self.target_x = (self.pos_x + self.finish_x) / 2
            self.steps = 0
            self.done = False
            print("\n[DICHOTOMIE] --- RESET ---", flush=True)
            print("[DICHOTOMIE] Étape |  +Δ (m)   |  parcouru (m)  |  reste (m)", flush=True)

    def update(self, dt):
        if self.done:
            return
        dx = self.speed * dt
        if self.pos_x + dx >= self.target_x:
            # log terminal
            prev_x = self.pos_x
            self.pos_x = self.target_x
            self.steps += 1

            parcouru_px = self.pos_x - self.start_x
            reste_px    = self.finish_x - self.pos_x
            delta_px    = self.pos_x - prev_x

            parcouru_m = parcouru_px * self.m_per_px
            reste_m    = max(0.0, reste_px * self.m_per_px)
            delta_m    = delta_px * self.m_per_px

            print(f"[DICHOTOMIE] {self.steps:5d} | {delta_m:10.6f} | {parcouru_m:14.6f} | {reste_m:10.6f}", flush=True)

            if abs(self.finish_x - self.pos_x) <= self.epsilon:
                self.done = True
                print("[DICHOTOMIE] ✓ Convergence (reste <= epsilon).", flush=True)
            else:
                self.target_x = (self.pos_x + self.finish_x) / 2
        else:
            self.pos_x += dx

    def draw(self):
        surf = self.screen
        surf.fill(BG)

        # piste
        pg.draw.line(surf, GREY, (MARGIN_LEFT, self.y), (self.W - MARGIN_RIGHT, self.y), 3)

        # graduations 1 m
        for m in range(0, int(DISTANCE_M) + 1):
            xg = int(self.start_x + m * (self.distance_px / DISTANCE_M))
            pg.draw.line(surf, GREY, (xg, self.y - 8), (xg, self.y + 8), 1)
            surf.blit(self.font.render(f"{m} m", True, GREY), (xg - 10, self.y + 12))

        # arbre (cible)
        if self.arbre_ok:
            rect = self.arbre_img.get_rect(midbottom=(self.finish_x, self.y + 2))
            surf.blit(self.arbre_img, rect)
        else:
            pg.draw.line(surf, (200, 30, 30), (self.finish_x, self.y - 50), (self.finish_x, self.y + 50), 3)

        # pierre
        if self.pierre_ok:
            rect = self.pierre_img.get_rect(midbottom=(int(self.pos_x), self.y + 2))
            surf.blit(self.pierre_img, rect)
        else:
            pg.draw.circle(surf, (100, 180, 220), (int(self.pos_x), self.y), 12)

        # textes
        title = self.font.render("Paradoxe de la dichotomie (Pierre -> Arbre)", True, WHITE)
        surf.blit(title, (self.W//2 - title.get_width()//2, 20))
        info = self.font.render(f"Étapes: {self.steps} | Reset: R | ESC: menu", True, WHITE)
        surf.blit(info, (20, self.H - 28))
