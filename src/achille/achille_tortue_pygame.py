# src/achille/achille_tortue_pygame.py
import sys
from pathlib import Path
import pygame as pg

# --- rendre 'src/' importable pour faire from achille.achille_tortue import simulate
THIS = Path(__file__).resolve()
SRC_DIR = THIS.parents[1]
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from achille.achille_tortue import simulate  # <-- TON ALGO

# -----------------------------
# Paramètres de simulation (garde tes valeurs)
# -----------------------------
V_ACHILLE  = 5.0
V_TORTUE   = 2.0
LEAD       = 20.0
DT         = 0.05
T_MAX      = 60.0
TIME_SCALE = 1.0   # 1.0 = temps réel (augmente si tu veux accélérer)
SCALE_M2PX = 10    # 1 m = 10 px (uniquement pour l'affichage graduations)

# -----------------------------
# Couleurs
# -----------------------------
BG    = (25, 28, 35)
GREY  = (90, 100, 115)
WHITE = (240, 240, 240)
BLUE  = (110, 160, 255)
GREEN = (100, 200, 120)
YELL  = (240, 200, 80)

# -----------------------------
# Sprites
# -----------------------------
ASSETS_DIR = THIS.parents[2] / "assets"   # adapte si ton dossier est ailleurs
ACHILLE_IMG_PATH = ASSETS_DIR / "achille.png"
TORTUE_IMG_PATH  = ASSETS_DIR / "tortue.png"

def _load_sprite(path: Path, size=(48, 48)):
    try:
        img = pg.image.load(str(path)).convert_alpha()
        if size:
            img = pg.transform.smoothscale(img, size)
        return img, True
    except Exception as e:
        print(f"[WARN] sprite introuvable: {path} -> {e}", flush=True)
        return None, False


class AchilleScene:
    """Classe uniforme (update/draw/handle_event) -> compatible avec zenon_menu."""
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.margin_left, self.margin_right = 60, 40
        self.line_y = self.H // 2  # piste au milieu
        self.font = pg.font.SysFont("consolas", 18)

        # sprites
        self.achille_sprite, self.achille_ok = _load_sprite(ACHILLE_IMG_PATH, (48, 48))
        self.tortue_sprite,  self.tortue_ok  = _load_sprite(TORTUE_IMG_PATH,  (48, 48))

        # trajectoire depuis TON algo
        self._build_trajectory()

        # état d'animation
        self.sim_time = 0.0
        self.idx_anim = 0
        self.caught_runtime = False
        self.x_a = 0.0
        self.x_t = LEAD
        self.t   = 0.0

        # ---------- LOGGER TERMINAL ----------
        self.LOG_EVERY  = 0.1   # log toutes les 0.1 s simulées
        self.next_log_t = 0.0
        print("\n[ACHILLE] t (s) | Achille (m) | Tortue (m)", flush=True)

    def _build_trajectory(self):
        self.results, (self.caught_final, self.t_hit_final, self.x_hit_final) = simulate(
            v_achille=V_ACHILLE,
            v_tortue=V_TORTUE,
            lead=LEAD,
            dt=DT,
            t_max=T_MAX,
        )

    def _interp_at(self, target_t: float, start_idx=0):
        """Interpolation linéaire position Achille/Tortue à l'instant target_t."""
        n = len(self.results)
        i = start_idx
        while i + 1 < n and self.results[i + 1][0] <= target_t:
            i += 1

        t_i, xa_i, xt_i = self.results[i]
        if i + 1 < n:
            t_j, xa_j, xt_j = self.results[i + 1]
            if t_j == t_i:
                return target_t, xa_i, xt_i, i
            alpha = (target_t - t_i) / (t_j - t_i)
            x_a = xa_i + alpha * (xa_j - xa_i)
            x_t = xt_i + alpha * (xt_j - xt_i)
            return target_t, x_a, x_t, i
        else:
            return self.results[-1][0], self.results[-1][1], self.results[-1][2], i

    # --- events transmis par le menu
    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_r:
            # reset animation + trajectoire (garde tes paramètres)
            self.sim_time = 0.0
            self.idx_anim = 0
            self.caught_runtime = False
            self._build_trajectory()
            self.next_log_t = 0.0
            print("\n[ACHILLE] --- RESET ---", flush=True)
            print("[ACHILLE] t (s) | Achille (m) | Tortue (m)", flush=True)

    def update(self, dt: float):
        # avancer le temps simulé
        self.sim_time += dt * TIME_SCALE
        if self.sim_time > self.results[-1][0]:
            self.sim_time = self.results[-1][0]

        # --- logs terminal à intervalles réguliers ---
        while self.next_log_t <= self.sim_time and self.next_log_t <= self.results[-1][0]:
            tL, xAL, xTL, self.idx_anim = self._interp_at(self.next_log_t, start_idx=self.idx_anim)
            print(f"[ACHILLE] {tL:7.2f} | {xAL:11.2f} | {xTL:9.2f}", flush=True)
            self.next_log_t += self.LOG_EVERY

        # état courant pour l'affichage
        t, x_a, x_t, self.idx_anim = self._interp_at(self.sim_time, start_idx=self.idx_anim)
        self.x_a, self.x_t, self.t = x_a, x_t, t
        if not self.caught_runtime and x_a >= x_t:
            self.caught_runtime = True

    def draw(self):
        surf = self.screen
        surf.fill(BG)

        # piste
        pg.draw.line(surf, GREY, (self.margin_left, self.line_y),
                               (self.W - self.margin_right, self.line_y), 3)

        # graduations en mètres (optionnel, basé sur SCALE_M2PX)
        max_m = int((self.W - self.margin_left - self.margin_right) / SCALE_M2PX)
        for m in range(0, max_m + 1, 10):
            xg = self.margin_left + m * SCALE_M2PX
            pg.draw.line(surf, GREY, (xg, self.line_y - 10), (xg, self.line_y + 10), 1)
            surf.blit(self.font.render(f"{m} m", True, GREY), (xg - 14, self.line_y + 14))

        # conversion m -> px pour placer les sprites
        x_a_px = min(self.margin_left + int(self.x_a * SCALE_M2PX), self.W - self.margin_right)
        x_t_px = min(self.margin_left + int(self.x_t * SCALE_M2PX), self.W - self.margin_right)

        # Achille posé sur la ligne (midbottom = bas du sprite collé à la piste)
        if self.achille_ok:
            ach_rect = self.achille_sprite.get_rect(midbottom=(x_a_px, self.line_y + 2))
            surf.blit(self.achille_sprite, ach_rect)
        else:
            pg.draw.circle(surf, BLUE, (x_a_px, self.line_y), 12)

        # Tortue posée sur la ligne
        if self.tortue_ok:
            tor_rect = self.tortue_sprite.get_rect(midbottom=(x_t_px, self.line_y + 2))
            surf.blit(self.tortue_sprite, tor_rect)
        else:
            pg.draw.circle(surf, GREEN, (x_t_px, self.line_y), 12)

        # Infos
        info = f"t={self.t:5.2f}s | xA={self.x_a:6.2f} m | xT={self.x_t:6.2f} m | vA={V_ACHILLE} | vT={V_TORTUE}"
        surf.blit(self.font.render(info, True, WHITE), (20, 12))

        if self.caught_runtime:
            surf.blit(self.font.render("✅ Rattrapée (animation)", True, YELL), (20, self.H - 36))
            if self.caught_final:
                surf.blit(self.font.render(
                    f"t_hit (algo) ≈ {self.t_hit_final:.2f}s, x ≈ {self.x_hit_final:.2f} m",
                    True, WHITE), (20, self.H - 18))
