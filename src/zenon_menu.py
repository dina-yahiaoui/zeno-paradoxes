# src/zenon_menu.py
import sys
import pygame as pg
from pathlib import Path

THIS = Path(__file__).resolve()
SRC_DIR = THIS.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from achille.achille_tortue_pygame import AchilleScene
from dichotomie.dichotomie_pygame import DichotomieScene
from fleche.fleche_pygame import FlecheScene

ASSETS_DIR = THIS.parent.parent / "assets"
BG_MENU_PATH = ASSETS_DIR / "background_menu.png"

def rounded_rect_alpha(surf, rect, color, radius=14, border=0, border_color=(0,0,0,0)):
    tmp = pg.Surface((rect.w, rect.h), pg.SRCALPHA)
    pg.draw.rect(tmp, color, tmp.get_rect(), border_radius=radius)
    if border > 0:
        pg.draw.rect(tmp, border_color, tmp.get_rect(), width=border, border_radius=radius)
    surf.blit(tmp, rect.topleft)

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.W, self.H = screen.get_size()
        self.font_title = pg.font.SysFont("arial", 30, bold=True)
        self.font_btn = pg.font.SysFont("arial", 28)

        self.buttons = [
            ("Achille & la tortue", AchilleScene),
            ("Dichotomie", DichotomieScene),
            ("La Flèche", FlecheScene),
            ("Quitter", None),
        ]

        self.bg_menu = None
        try:
            img = pg.image.load(str(BG_MENU_PATH)).convert()
            self.bg_menu = pg.transform.scale(img, (self.W, self.H))
        except Exception as e:
            print(f"[WARN] Impossible de charger le fond du menu: {e}")

        # boutons centrés sans panneau
        self.btn_w = 360
        self.btn_h = 54
        self.btn_spacing = 72
        self.btn_start_y = int(self.H * 0.30)
        self.btn_x = self.W//2 - self.btn_w//2

        self.col_btn = (245, 241, 235, 220)
        self.col_btn_hover = (255, 252, 248, 255)
        self.col_btn_border = (0, 0, 0, 40)
        self.col_title = (245, 245, 245)
        self.col_btn_text = (35, 35, 35)

        self._hand = False

    def run(self):
        clock = pg.time.Clock()
        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            mx, my = pg.mouse.get_pos()
            hovering_any = False

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    for i, (label, SceneClass) in enumerate(self.buttons):
                        rect = pg.Rect(self.btn_x, self.btn_start_y + i*self.btn_spacing, self.btn_w, self.btn_h)
                        if rect.collidepoint(mx, my):
                            if SceneClass is None:
                                running = False
                            else:
                                self.launch_scene(SceneClass)

            for i in range(len(self.buttons)):
                rect = pg.Rect(self.btn_x, self.btn_start_y + i*self.btn_spacing, self.btn_w, self.btn_h)
                if rect.collidepoint(mx, my):
                    hovering_any = True
                    break
            if hovering_any and not self._hand:
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_HAND); self._hand = True
            elif not hovering_any and self._hand:
                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW); self._hand = False

            self.draw(mx, my)

        pg.quit(); sys.exit()

    def draw(self, mx, my):
        if self.bg_menu:
            self.screen.blit(self.bg_menu, (0, 0))
        else:
            self.screen.fill((240, 240, 240))

        # titre
        title = "Paradoxes de Zénon"
        t_img = self.font_title.render(title, True, self.col_title)
        self.screen.blit(t_img, t_img.get_rect(center=(self.W//2, int(self.H*0.25))))

        # boutons
        for i, (label, _) in enumerate(self.buttons):
            rect = pg.Rect(self.btn_x, self.btn_start_y + i*self.btn_spacing, self.btn_w, self.btn_h)
            hovered = rect.collidepoint(mx, my)

            shadow = rect.copy(); shadow.x += 2; shadow.y += 4
            rounded_rect_alpha(self.screen, shadow, (0,0,0,45), radius=16)

            rounded_rect_alpha(self.screen, rect,
                               self.col_btn_hover if hovered else self.col_btn,
                               radius=16, border=2, border_color=self.col_btn_border)

            txt = self.font_btn.render(label, True, self.col_btn_text)
            self.screen.blit(txt, txt.get_rect(center=rect.center))

        pg.display.flip()

    def launch_scene(self, SceneClass):
        clock = pg.time.Clock()
        scene = SceneClass(self.screen)
        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit(); sys.exit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    running = False
                if hasattr(scene, "handle_event"):
                    scene.handle_event(event)
            scene.update(dt)
            scene.draw()
            pg.display.flip()

if __name__ == "__main__":
    pg.init()
    screen = pg.display.set_mode((1000, 600))
    pg.display.set_caption("Paradoxes de Zénon")
    menu = Menu(screen)
    menu.run()
