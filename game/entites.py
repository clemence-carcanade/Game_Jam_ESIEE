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

    def __init__(self, x, xmin, xmax, y, image="marche", vitesse=2.2, force=16):
        self._droite, self._gauche = frames(image)
        # on cale la taille sur la hauteur de la frame (les planches 16 px sont
        # agrandies plus fort que celles de 32 px, pour des chats homogenes)
        echelle = 2.4 * 32 / self._droite[0].height
        super().__init__(self._droite[0], scale=echelle, center_x=x)
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
            chat.change_y = 13
            self._recharge = 0.55
            return True
        return False


class ChatNoir(arcade.Sprite):
    """Le chat noir du niveau 2 : immobile, il danse pour attirer le chat.

    Ce n'est pas un ennemi qui tue : c'est la sortie. Atteindre le chat noir et
    faire E, c'est se laisser emporter -- griller une vie, gagner le niveau.
    Toute la difficulte est d'arriver jusqu'a lui malgre la nuee de pousseurs.
    """

    def __init__(self, x, y):
        self._frames = []
        i = 0
        while True:
            chemin = C.DOSSIER_IMAGES / "chat_noir" / f"dance_{i}.png"
            if not chemin.is_file():
                break
            self._frames.append(arcade.load_texture(chemin))
            i += 1
        if not self._frames:
            self._frames = [arcade.Texture.create_empty("noir", (32, 40), (20, 20, 26))]
        super().__init__(self._frames[0], scale=3.0, center_x=x)
        self.bottom = y
        self._t = 0.0

    def mettre_a_jour(self, delta_time):
        self._t += delta_time
        self.texture = self._frames[int(self._t * 8) % len(self._frames)]


class Fille(arcade.Sprite):
    """La petite fille du niveau 3 : elle poursuit le chat sans relache.

    Des qu'elle le rattrape, elle le maquille (le chat vire au rose), puis le
    balance a l'autre bout de la piece. Elle ne tue pas -- elle empeche juste
    d'atteindre l'aquarium. Il faut la semer, ou aller plus vite qu'elle.
    """

    def __init__(self, x, y, vitesse=4.4):
        # la petite fille animee : les frames de marche extraites des planches
        self._anim = {}
        for nom in ("droite", "gauche"):
            frames = []
            i = 0
            while (C.DOSSIER_IMAGES / "fille" / f"{nom}_{i}.png").is_file():
                frames.append(arcade.load_texture(C.DOSSIER_IMAGES / "fille" / f"{nom}_{i}.png"))
                i += 1
            self._anim[nom] = frames or [arcade.Texture.create_empty("f", (32, 48), (150, 80, 160))]
        super().__init__(self._anim["droite"][0], scale=0.35, center_x=x)
        self.bottom = y
        self.sol = y
        self.vitesse = vitesse
        self._t = 0.0
        self._recharge = 0.0

    def mettre_a_jour(self, delta_time, chat):
        self._t += delta_time
        self._recharge = max(0.0, self._recharge - delta_time)

        # elle fonce vers le chat, sans relache, et le suit meme en hauteur
        direction = 1 if chat.center_x > self.center_x else -1
        self.center_x += self.vitesse * direction
        # elle grimpe vite vers l'etage du chat (impossible de la semer en montant)
        self.center_y += (chat.center_y - self.center_y) * 0.10

        jeu = self._anim["droite"] if direction > 0 else self._anim["gauche"]
        self.texture = jeu[int(self._t * 8) % len(jeu)]

        # elle rattrape le chat : maquillage + projection violente a l'autre bout
        if self._recharge <= 0 and chat.vivant and arcade.check_for_collision(self, chat):
            chat.color = (255, 150, 200)                 # maquille en rose
            loin = 1 if chat.center_x < self.center_x else -1
            chat.change_x = 26 * loin                    # balance brutalement, tres loin
            chat.change_y = 20
            self._recharge = 0.7                         # elle recommence vite
            return True
        return False
