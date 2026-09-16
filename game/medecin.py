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
DUREE_SOMMEIL = 7.0                 # les somniferes ne l'assomment qu'un temps


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
        self._sommeil = 0.0         # temps de sommeil restant
        self._retour_prevu = False  # apres un soin, il retourne a son poste
        self._pause = 0.0
        self._image = 0
        self._minuteur = 0.0

    # ------------------------------------------------------------------
    def soigner(self, x_du_chat: float) -> None:
        """Il ne se deplace pas : il SURGIT directement sur le chat, le recoud,
        puis repart aussitot a son poste."""
        if self.endormi:
            return
        self.center_x = x_du_chat            # il apparait pile sur le chat
        self.bottom = self.sol
        self._pause = DUREE_SOIN
        self._retour_prevu = True

    def endormir(self) -> None:
        """Les somniferes le terrassent... mais seulement pour un temps."""
        self.endormi = True
        self._sommeil = DUREE_SOMMEIL
        self._pause = 0.0
        self._retour_prevu = False
        self.angle = 90                      # allonge par terre
        self.color = (205, 205, 230)
        self.center_y = self.sol + self.width / 2 - 14

    def se_reveiller(self) -> None:
        """Le somnifere se dissipe : il se releve a son poste."""
        self.endormi = False
        self._sommeil = 0.0
        self._pause = 0.0
        self._retour_prevu = False
        self.center_x = self.poste_x
        self.angle = 0
        self.color = (255, 255, 255)
        self.bottom = self.sol

    @property
    def ratio_sommeil(self) -> float:
        """Part de sommeil restante (1 -> 0), pour la barre de compte a rebours."""
        return max(0.0, self._sommeil / DUREE_SOMMEIL) if self.endormi else 0.0

    # ------------------------------------------------------------------
    def mettre_a_jour(self, delta_time: float, chat=None) -> None:
        if self.endormi:
            self._sommeil -= delta_time
            if self._sommeil <= 0:
                self.se_reveiller()
            return

        self._minuteur += delta_time

        # il ne patrouille jamais : il reste a son poste. La seule fois ou il
        # bouge, c'est pour surgir sur le chat (soigner), puis il y retourne.
        if self._pause > 0:
            self._pause -= delta_time
            if self._pause <= 0 and self._retour_prevu:
                self.center_x = self.poste_x
                self._retour_prevu = False

        frames = self.animations["repos"]
        if self._minuteur >= 0.45:
            self._minuteur = 0.0
            self._image += 1
        self.texture = frames[self._image % len(frames)]
        self.bottom = self.sol
        self.bottom = self.sol
