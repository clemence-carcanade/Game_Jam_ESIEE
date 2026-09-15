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

from game import animations
from game import constantes as C


class Chat(arcade.Sprite):
    def __init__(self, x: float, y: float, anime: bool = True):
        """Le chat est anime si ``assets/images/chat.png`` est la ; sinon c'est
        un carre orange, et le jeu tourne quand meme.

        La **boite de collision ne depend jamais de l'image** : une case
        d'animation fait 32 x 32 alors que le chat n'occupe qu'un petit
        rectangle en bas de la case. Sans ça il flotterait au-dessus du sol et
        mourrait parce qu'un pixel transparent a touche un pic.
        """
        self.anime = anime and (C.DOSSIER_IMAGES / "chat.png").is_file()

        if self.anime:
            super().__init__(
                animations.images("repos")[0],
                scale=C.ECHELLE_CHAT, center_x=x, center_y=y,
            )
            largeur, hauteur, decalage = animations.boite_du_chat("repos")
            self.definir_boite_de_collision(largeur, hauteur, decalage)
        else:
            carre = arcade.Texture.create_empty(
                "chat", (C.LARGEUR_CHAT, C.HAUTEUR_CHAT), C.COULEUR_CHAT
            )
            super().__init__(carre, center_x=x, center_y=y)
            self.definir_boite_de_collision(C.LARGEUR_CHAT, C.HAUTEUR_CHAT)

        # --- animation en cours ---
        self.vivant = True
        self._animation = "repos"
        self._image = 0
        self._minuteur_image = 0.0
        self._minuteur_reception = 0.0

        self.depart_x = x
        self.depart_y = y

        # --- intentions, remplies par le clavier ---
        self.veut_gauche = False
        self.veut_droite = False
        self.veut_descendre = False

        # --- état ---
        self.regarde = 1            # 1 = droite, -1 = gauche
        self.au_sol = False
        self.sur_surface_glissante = False   # remis a jour a chaque image
        self.minuteur_sac = 0.0              # le chat a le sac de croquettes sur la tete

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
    @property
    def dans_le_sac(self) -> bool:
        return self.minuteur_sac > 0

    def coincer_dans_le_sac(self) -> None:
        """Faux piege : le chat fonce droit devant, sans rien voir."""
        self.minuteur_sac = C.DUREE_DANS_LE_SAC

    def liberer_du_sac(self) -> None:
        self.minuteur_sac = 0.0

    def calculer_deplacement(self, delta_time: float, au_sol: bool) -> None:
        self.au_sol = au_sol

        if self.dans_le_sac:
            # Il ne voit rien : il court droit devant et le joueur n'y peut rien.
            self.minuteur_sac -= delta_time
            self.veut_gauche = self.regarde < 0
            self.veut_droite = self.regarde > 0

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
        if self.sur_surface_glissante and au_sol:
            acceleration = C.GLISSE_ACCELERATION
        cible = direction * C.VITESSE_CHAT

        if direction:
            # on tend vers la vitesse voulue, sans la dépasser
            if self.change_x < cible:
                self.change_x = min(cible, self.change_x + acceleration)
            elif self.change_x > cible:
                self.change_x = max(cible, self.change_x - acceleration)
        else:
            # aucune touche : le chat freine (moins vite en l'air, presque pas
            # sur une surface glissante)
            freinage = C.FREINAGE if au_sol else C.FREINAGE * 0.3
            if self.sur_surface_glissante and au_sol:
                freinage = C.GLISSE_FREINAGE
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
    def definir_boite_de_collision(self, largeur, hauteur, decalage_y=0.0) -> None:
        """Force une boite de collision rectangulaire, independante de l'image.

        ``largeur``, ``hauteur`` et ``decalage_y`` sont en pixels de la planche
        (avant mise a l'echelle). Le decalage sert a recentrer la boite sur le
        chat, qui est dessine en bas de sa case.
        """
        demi_l, demi_h = largeur / 2, hauteur / 2
        self.hit_box = arcade.hitbox.HitBox(
            (
                (-demi_l, decalage_y - demi_h),
                (demi_l, decalage_y - demi_h),
                (demi_l, decalage_y + demi_h),
                (-demi_l, decalage_y + demi_h),
            ),
            position=(self.center_x, self.center_y),
            scale=(self.scale_x, self.scale_y),
        )

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------
    def signaler_atterrissage(self) -> None:
        """Le moteur de collisions previent qu'on vient de toucher le sol."""
        self._minuteur_reception = 0.18

    def _animation_voulue(self) -> str:
        if not self.vivant:
            return "allonge"
        if not self.au_sol:
            return "saut" if self.change_y > 0 else "chute"
        if self._minuteur_reception > 0:
            return "reception"
        if abs(self.change_x) > 0.5:
            return "marche"
        return "repos"

    def mettre_a_jour_animation(self, delta_time: float) -> None:
        """Choisit l'animation et fait defiler ses images."""
        if not self.anime:
            return

        self._minuteur_reception = max(0.0, self._minuteur_reception - delta_time)

        voulue = self._animation_voulue()
        if voulue != self._animation:
            self._animation = voulue
            self._image = 0
            self._minuteur_image = 0.0

        images = animations.images(self._animation, vers_la_gauche=self.regarde < 0)

        self._minuteur_image += delta_time
        if self._minuteur_image >= animations.duree(self._animation):
            self._minuteur_image = 0.0
            if self._image + 1 < len(images):
                self._image += 1
            elif animations.en_boucle(self._animation):
                self._image = 0

        self.texture = images[self._image]

    def replacer_au_depart(self) -> None:
        """Remet le chat à sa position de départ (nouvelle vie, redémarrage)."""
        self.center_x = self.depart_x
        self.center_y = self.depart_y
        self.change_x = 0.0
        self.change_y = 0.0
        self._coyote = 0.0
        self._saut_memorise = 0.0
