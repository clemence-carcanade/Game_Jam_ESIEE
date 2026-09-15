"""Les entites mobiles qui embetent le chat : les Pousseurs.

Dans Sept Vies, le but est de mourir. Les "ennemis" ne tuent donc pas : ils
PROTEGENT le chat malgre lui. Un Pousseur patrouille en continu et, des qu'il
touche le chat, le repousse loin du danger. Le joueur doit ruser, aller vite,
les semer pour atteindre le piege. C'est ce qui rend le niveau vivant a jouer.
"""

import math

import arcade

from game import constantes as C


class Pousseur(arcade.Sprite):
    """Un chat (ou un maitre) qui fait l'aller-retour et bouscule le joueur."""

    def __init__(self, x, xmin, xmax, y, image="chat_gris", vitesse=2.2, force=16):
        chemin = C.DOSSIER_IMAGES / "decor" / f"{image}.png"
        texture = arcade.load_texture(chemin) if chemin.is_file() else \
            arcade.Texture.create_empty("pousseur", (24, 16), (150, 150, 160))
        super().__init__(texture, scale=3.0, center_x=x)
        self.bottom = y
        self.sol = y
        self.xmin, self.xmax = xmin, xmax
        self.vitesse = vitesse
        self.force = force
        self.sens = 1
        self._t = 0.0
        self._recharge = 0.0
        self._textures = (texture, texture.flip_left_right())

    def mettre_a_jour(self, delta_time, chat):
        self._t += delta_time
        self._recharge = max(0.0, self._recharge - delta_time)

        # patrouille : aller-retour entre les bornes
        self.center_x += self.vitesse * self.sens
        if self.center_x <= self.xmin:
            self.center_x, self.sens = self.xmin, 1
        elif self.center_x >= self.xmax:
            self.center_x, self.sens = self.xmax, -1

        # une petite demarche qui sautille + regard dans le sens de marche
        self.bottom = self.sol + abs(math.sin(self._t * 8)) * 3
        self.texture = self._textures[0 if self.sens > 0 else 1]

        # au contact du chat : on le repousse (on ne le tue pas, on le protege)
        if self._recharge <= 0 and chat.vivant and arcade.check_for_collision(self, chat):
            direction = 1 if chat.center_x >= self.center_x else -1
            chat.change_x = self.force * direction
            chat.change_y = 8
            self._recharge = 0.7
            return True          # a pousse le chat, cette image
        return False
