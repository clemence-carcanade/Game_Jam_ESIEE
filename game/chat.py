"""Le chat : ses déplacements, ses réflexes, ses cicatrices.

Le chat n'impose pas sa position : il calcule seulement ses vitesses
(``change_x`` / ``change_y``). C'est le moteur de collisions qui le déplace
vraiment et qui décide de ce qu'il touche.

Ses trois réflexes sont de simples booléens. Ce sont eux qui rendent le chat
difficile à tuer — les niveaux doivent les désactiver pour être résolus :

    reflexe_pattes      il retombe sur ses pattes            (l'étourdir)
    reflexe_moustaches  il esquive ce qui est mortel         (couper les moustaches)
    reflexe_agrippe     il s'accroche au rebord              (scotcher ses pattes)
"""

import arcade

from game import constantes as C


class Chat(arcade.Sprite):
    def __init__(self, x: float, y: float, texture=None, echelle: float = 1.0):
        """``texture`` est optionnelle : sans elle, le chat est un carré orange.

        Quand les sprites du pack d'animations arriveront, il suffira de passer
        la texture ici. La **boîte de collision reste la même** : les images
        d'animation ont presque toujours du vide autour du personnage, et on ne
        veut pas que le chat meure parce qu'un pixel transparent a touché un pic.
        """
        if texture is None:
            texture = arcade.Texture.create_empty(
                "chat", (C.LARGEUR_CHAT, C.HAUTEUR_CHAT), C.COULEUR_CHAT
            )
        super().__init__(texture, scale=echelle, center_x=x, center_y=y)
        self.definir_boite_de_collision(C.LARGEUR_CHAT, C.HAUTEUR_CHAT)

        self.depart_x = x
        self.depart_y = y

        # --- intentions, remplies par le clavier ---
        self.veut_gauche = False
        self.veut_droite = False
        self.veut_descendre = False

        # --- état ---
        self.regarde = 1            # 1 = droite, -1 = gauche
        self.au_sol = False

        # --- réflexes (actifs au départ : c'est tout le problème du joueur) ---
        self.reflexe_pattes = True
        self.reflexe_moustaches = True
        self.reflexe_agrippe = True

        # --- cicatrices héritées des vies précédentes (rempli par vies.py) ---
        self.cicatrices = []

        # --- minuteries internes du saut ---
        self._coyote = 0.0
        self._saut_memorise = 0.0

    # ------------------------------------------------------------------
    # Intentions envoyées par le clavier
    # ------------------------------------------------------------------
    def demander_saut(self) -> None:
        """Touche de saut enfoncée : on mémorise la demande."""
        self._saut_memorise = C.MEMOIRE_SAUT

    def relacher_saut(self) -> None:
        """Touche relâchée tôt : le saut est plus court."""
        if self.change_y > 0:
            self.change_y *= C.COUPURE_SAUT

    # ------------------------------------------------------------------
    # Calcul des vitesses (appelé avant le moteur de collisions)
    # ------------------------------------------------------------------
    def calculer_deplacement(self, delta_time: float, au_sol: bool) -> None:
        self.au_sol = au_sol

        if au_sol:
            self._coyote = C.TEMPS_COYOTE
        else:
            self._coyote = max(0.0, self._coyote - delta_time)
        self._saut_memorise = max(0.0, self._saut_memorise - delta_time)

        self._deplacement_horizontal(au_sol)
        self._sauter()

        if self.change_y < -C.VITESSE_CHUTE_MAX:
            self.change_y = -C.VITESSE_CHUTE_MAX

    def _deplacement_horizontal(self, au_sol: bool) -> None:
        direction = int(self.veut_droite) - int(self.veut_gauche)
        if direction:
            self.regarde = direction

        acceleration = C.ACCELERATION_SOL if au_sol else C.ACCELERATION_AIR
        cible = direction * C.VITESSE_CHAT

        if direction:
            # on tend vers la vitesse voulue, sans la dépasser
            if self.change_x < cible:
                self.change_x = min(cible, self.change_x + acceleration)
            elif self.change_x > cible:
                self.change_x = max(cible, self.change_x - acceleration)
        else:
            # aucune touche : le chat freine (moins vite en l'air)
            freinage = C.FREINAGE if au_sol else C.FREINAGE * 0.3
            if abs(self.change_x) <= freinage:
                self.change_x = 0.0
            elif self.change_x > 0:
                self.change_x -= freinage
            else:
                self.change_x += freinage

    def _sauter(self) -> None:
        if self._saut_memorise > 0 and self._coyote > 0:
            self.change_y = C.VITESSE_SAUT
            self._saut_memorise = 0.0
            self._coyote = 0.0

    # ------------------------------------------------------------------
    def definir_boite_de_collision(self, largeur: float, hauteur: float) -> None:
        """Force une boîte de collision rectangulaire, indépendante de l'image.

        À rappeler si on change d'échelle ou de pack de sprites.
        """
        demi_l = largeur / 2 / self.scale_x
        demi_h = hauteur / 2 / self.scale_y
        self.hit_box = arcade.hitbox.HitBox(
            ((-demi_l, -demi_h), (demi_l, -demi_h), (demi_l, demi_h), (-demi_l, demi_h)),
            position=(self.center_x, self.center_y),
            scale=(self.scale_x, self.scale_y),
        )

    def replacer_au_depart(self) -> None:
        """Remet le chat à sa position de départ (nouvelle vie, redémarrage)."""
        self.center_x = self.depart_x
        self.center_y = self.depart_y
        self.change_x = 0.0
        self.change_y = 0.0
        self._coyote = 0.0
        self._saut_memorise = 0.0
