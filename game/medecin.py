"""Le medecin du niveau 6, anime avec la planche lablady.

Il veille a son poste. Chaque fois que le chat tente de se tuer, il marche
jusqu'a lui, le soigne, et retourne a son poste. Pour gagner le niveau, il faut
lui faire tomber les somniferes dessus : endormi, il ne soigne plus rien, et
chacune de ses methodes de soin devient une vraie fin.
"""

import arcade

from game import constantes as C

DOSSIER = C.DOSSIER_IMAGES / "medecin"
ECHELLE = 4.0                       # frames de 31 px -> ~2 cases de haut
VITESSE = 5.0                       # il marche vite, c'est un urgentiste
DUREE_SOIN = 0.9                    # le temps de recoudre


def _frames(nom):
    textures = []
    for i in range(8):
        chemin = DOSSIER / f"{nom}_{i}.png"
        if not chemin.is_file():
            break
        textures.append(arcade.load_texture(chemin))
    return textures


class Medecin(arcade.Sprite):
    def __init__(self, x: float, sol: float):
        self.animations = {
            "repos": _frames("idle_bas"),
            "droite": _frames("marche_droite"),
            "gauche": _frames("marche_gauche"),
        }
        super().__init__(self.animations["repos"][0], scale=ECHELLE, center_x=x)
        self.sol = sol
        self.bottom = sol
        self.poste_x = x

        self.endormi = False
        self._etapes = []           # les x ou aller, dans l'ordre
        self._pause = 0.0
        self._image = 0
        self._minuteur = 0.0

    # ------------------------------------------------------------------
    def soigner(self, x_du_chat: float) -> None:
        """Il accourt, recoud, et retourne a son poste."""
        if self.endormi:
            return
        self._etapes = [x_du_chat, self.poste_x]
        self._pause = 0.0

    def endormir(self) -> None:
        """Les somniferes ont gagne : il glisse de sa chaise et ronfle."""
        self.endormi = True
        self._etapes = []
        self.angle = 90                      # allonge par terre
        self.color = (205, 205, 230)
        self.center_y = self.sol + self.width / 2 - 14

    @property
    def occupe(self) -> bool:
        return bool(self._etapes)

    # ------------------------------------------------------------------
    def mettre_a_jour(self, delta_time: float) -> None:
        if self.endormi:
            return

        self._minuteur += delta_time
        animation = "repos"

        if self._pause > 0:
            self._pause -= delta_time
        elif self._etapes:
            cible = self._etapes[0]
            ecart = cible - self.center_x
            if abs(ecart) <= VITESSE:
                self.center_x = cible
                self._etapes.pop(0)
                if self._etapes:             # il vient d'atteindre le chat
                    self._pause = DUREE_SOIN
            else:
                self.center_x += VITESSE if ecart > 0 else -VITESSE
                animation = "droite" if ecart > 0 else "gauche"

        frames = self.animations[animation] or self.animations["repos"]
        cadence = 0.12 if animation != "repos" else 0.45
        if self._minuteur >= cadence:
            self._minuteur = 0.0
            self._image += 1
        self.texture = frames[self._image % len(frames)]
        self.bottom = self.sol
