"""L'intro video jouee au lancement du jeu, avant le menu.

La video a ete decoupee en images (assets/images/intro/) par un script ; on les
joue en sequence a 12 images/seconde, puis on passe au menu. Une touche ou un
clic passe l'intro.
"""

from pathlib import Path

import arcade

from game import constantes as C

DOSSIER = C.DOSSIER_IMAGES / "intro"
CADENCE = 1 / 12.0            # 12 images par seconde


class IntroView(arcade.View):
    def __init__(self):
        super().__init__()
        self.frames = [
            arcade.load_texture(p) for p in sorted(DOSSIER.glob("frame_*.jpg"))
        ]
        self.index = 0
        self.minuteur = 0.0

    def on_show_view(self):
        self.window.background_color = arcade.color.BLACK
        self._lecteur = None
        son = C.DOSSIER_SONS / "intro.mp3"
        if son.is_file():
            try:
                from game import audio as _a
                self._lecteur = arcade.play_sound(arcade.Sound(son), volume=_a.VOLUME)
            except Exception:
                self._lecteur = None

    def _arreter_son(self):
        if getattr(self, "_lecteur", None) is not None:
            try:
                arcade.stop_sound(self._lecteur)
            except Exception:
                pass
            self._lecteur = None

    def on_update(self, delta_time):
        if not self.frames:
            self._suite()
            return
        self.minuteur += delta_time
        if self.minuteur >= CADENCE:
            self.minuteur -= CADENCE
            self.index += 1
            if self.index >= len(self.frames):
                self._suite()

    def on_draw(self):
        self.clear()
        if self.frames and self.index < len(self.frames):
            t = self.frames[self.index]
            arcade.draw_texture_rect(
                t, arcade.LBWH(0, 0, C.LARGEUR_FENETRE, C.HAUTEUR_FENETRE))
        arcade.draw_text("Espace / clic pour passer",
                         C.LARGEUR_FENETRE - 20, 20, (200, 200, 210, 180), 13,
                         anchor_x="right")

    def on_key_press(self, key, modifiers):
        self._suite()

    def on_mouse_press(self, x, y, button, modifiers):
        self._suite()

    def _suite(self):
        """Une fois l'intro finie (ou passee), on lance le jeu."""
        self._arreter_son()
        from game.jeu import VueJeu
        self.window.show_view(VueJeu(1))
