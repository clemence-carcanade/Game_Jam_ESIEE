"""Les entites mobiles qui embetent le chat : les Pousseurs.

Dans Sept Vies, le but est de mourir. Les "ennemis" ne tuent donc pas : ils
PROTEGENT le chat malgre lui. Un Pousseur patrouille en continu (marche animee)
et, des qu'il touche le chat, le repousse loin du danger. Le joueur doit ruser,
aller vite, les semer pour atteindre le piege.

Ils utilisent la planche assets/images/chats/ (marche de profil, 8 frames).
"""

import math

import arcade

from game import constantes as C

_FRAMES = {}


def frames(nom):
    """Les textures d'une animation de chat (marche/course), chargees une fois."""
    if nom not in _FRAMES:
        droite, gauche = [], []
        i = 0
        while True:
            chemin = C.DOSSIER_IMAGES / "chats" / f"{nom}_{i}.png"
            if not chemin.is_file():
                break
            t = arcade.load_texture(chemin)
            droite.append(t)
            gauche.append(t.flip_left_right())
            i += 1
        if not droite:                       # secours : le vieux chat gris
            secours = C.DOSSIER_IMAGES / "decor" / "chat_gris.png"
            t = (arcade.load_texture(secours) if secours.is_file()
                 else arcade.Texture.create_empty("c", (24, 16), (150, 150, 160)))
            droite, gauche = [t], [t.flip_left_right()]
        _FRAMES[nom] = (droite, gauche)
    return _FRAMES[nom]


class Pousseur(arcade.Sprite):
    """Un chat qui fait l'aller-retour anime et bouscule le joueur."""

    def __init__(self, x, xmin, xmax, y, image="chat_gris", vitesse=2.2, force=16):
        self._droite, self._gauche = frames("marche")
        super().__init__(self._droite[0], scale=2.4, center_x=x)
        self.bottom = y
        self.sol = y
        self.xmin, self.xmax = xmin, xmax
        self.vitesse = vitesse
        self.force = force
        self.sens = 1
        self._t = 0.0
        self._recharge = 0.0

    def mettre_a_jour(self, delta_time, chat):
        self._t += delta_time
        self._recharge = max(0.0, self._recharge - delta_time)

        self.center_x += self.vitesse * self.sens
        if self.center_x <= self.xmin:
            self.center_x, self.sens = self.xmin, 1
        elif self.center_x >= self.xmax:
            self.center_x, self.sens = self.xmax, -1

        # l'animation de marche defile a la cadence des pas
        jeu = self._droite if self.sens > 0 else self._gauche
        self.texture = jeu[int(self._t * 10) % len(jeu)]
        self.bottom = self.sol

        if self._recharge <= 0 and chat.vivant and arcade.check_for_collision(self, chat):
            direction = 1 if chat.center_x >= self.center_x else -1
            chat.change_x = self.force * direction
            chat.change_y = 8
            self._recharge = 0.7
            return True
        return False
