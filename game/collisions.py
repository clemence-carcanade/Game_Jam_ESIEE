"""Le moteur de collisions. C'est le seul endroit où on décide ce qui se touche.

Il gère cinq familles d'éléments, et il est volontairement indépendant des
graphismes : il ne manipule que des ``arcade.SpriteList``. Quand les vrais
sprites remplaceront les rectangles de couleur, ce fichier ne bougera pas.

    murs (#)          solides, on ne les traverse jamais
    plateformes (=)   traversables par le bas et par les côtés ; on ne peut
                      qu'atterrir dessus, et la touche bas fait redescendre
    mortels (X)       ce qui fait griller une vie au chat
    poussables (O)    poufs, caisses, paniers : ça se pousse et ça tombe
    zones (B, D...)   boutons, déclencheurs : détectés sans bloquer

Il applique aussi la règle de game design n°2 : **le corps du chat résiste**.
Trois réflexes, trois booléens portés par le chat, que les niveaux doivent
désactiver :

    reflexe_pattes      le chat retombe sur ses pattes (encaisse les chutes)
    reflexe_moustaches  ses moustaches lui font esquiver ce qui est mortel
    reflexe_agrippe     il s'agrippe au rebord, impossible de tomber en marchant

Ordre d'utilisation dans la boucle de jeu (ne pas intervertir) :

    au_sol = moteur.est_au_sol()          # 1. le chat sait s'il peut sauter
    chat.calculer_deplacement(dt, au_sol)  # 2. le chat calcule ses vitesses
    contacts = moteur.mettre_a_jour()      # 3. on déplace et on résout tout
    if contacts.mort:
        jeu.griller_une_vie(contacts.mort)
"""

from dataclasses import dataclass, field

import arcade

from game import constantes as C

#: tolérance verticale pour "poser le pied" sur une plateforme traversable
TOLERANCE_ATTERRISSAGE = 2.0

#: distance de test sous les pattes du chat pour savoir s'il est au sol
SONDE_SOL = 5.0

#: largeur de la sonde qui verifie que le chat est vraiment pose (pas en
#: equilibre sur un pixel de rebord). Sert au reflexe d'agrippement.
SONDE_CENTRE = 10.0


def _en_listes(valeur):
    """Accepte une SpriteList, une liste de SpriteList, ou rien du tout."""
    if valeur is None:
        return []
    if isinstance(valeur, arcade.SpriteList):
        return [valeur]
    return list(valeur)


@dataclass
class Contacts:
    """Ce qui s'est passé pendant une image. Retourné par ``mettre_a_jour()``."""

    au_sol: bool = False
    atterrissage: bool = False       # a touché le sol *cette image*
    hauteur_chute: float = 0.0       # hauteur de la chute qui vient de finir
    sur_plateforme: bool = False     # debout sur une plateforme traversable
    hors_niveau: bool = False        # tombé sous le niveau
    esquive: bool = False            # les moustaches ont sauvé le chat
    mortels: list = field(default_factory=list)
    zones: list = field(default_factory=list)
    mort: str = ""                   # "" si le chat est vivant, sinon la cause

    @property
    def vivant(self) -> bool:
        return self.mort == ""


class MoteurCollisions:
    def __init__(
        self,
        chat,
        murs=None,
        plateformes=None,
        mortels=None,
        poussables=None,
        zones=None,
        gravite=C.GRAVITE,
        bas_du_niveau=None,
        largeur_niveau=None,
    ):
        self.chat = chat
        self.murs = _en_listes(murs)
        self.plateformes = _en_listes(plateformes)
        self.mortels = _en_listes(mortels)
        self.poussables = _en_listes(poussables)
        self.zones = _en_listes(zones)
        self.gravite = gravite
        self.bas_du_niveau = (
            -C.MARGE_HORS_NIVEAU if bas_du_niveau is None else bas_du_niveau
        )
        # Sans cette limite, un chat qui saute par-dessus le mur du bord se
        # retrouve à marcher à côté du niveau. Les bords sont durs, point.
        self.largeur_niveau = largeur_niveau

        # Les murs "durs" et les objets poussables sont délégués au moteur
        # d'arcade : il sépare déjà proprement horizontal et vertical.
        self.moteur = arcade.PhysicsEnginePlatformer(
            chat, walls=self.murs + self.poussables, gravity_constant=gravite
        )

        self._etait_au_sol = False
        self._altitude_depart_chute = chat.center_y
        self._derniere_position_sure = (chat.center_x, chat.center_y)

        # petite sonde invisible, placee sous le centre du chat
        self._sonde = arcade.Sprite(
            arcade.Texture.create_empty("_sonde", (int(SONDE_CENTRE), int(SONDE_CENTRE)))
        )

    # ------------------------------------------------------------------
    # 1. Interrogation — AVANT que le chat calcule ses vitesses
    # ------------------------------------------------------------------
    def est_au_sol(self) -> bool:
        """Le chat a-t-il quelque chose de solide sous les pattes ?"""
        return self.moteur.can_jump(y_distance=SONDE_SOL) or self._touche_plateforme_dessous()

    def _touche_plateforme_dessous(self) -> bool:
        """On descend le chat de quelques pixels, on regarde, on le remet.

        C'est exactement la technique de ``can_jump()`` d'arcade, appliquée aux
        plateformes traversables que le moteur d'arcade ne connaît pas.
        """
        if self.chat.change_y > 0 or not self.plateformes:
            return False

        self.chat.center_y -= SONDE_SOL
        touche = any(
            arcade.check_for_collision_with_list(self.chat, liste)
            for liste in self.plateformes
        )
        self.chat.center_y += SONDE_SOL
        return touche

    # ------------------------------------------------------------------
    # 2. Résolution — APRÈS que le chat a calculé ses vitesses
    # ------------------------------------------------------------------
    def mettre_a_jour(self, descendre: bool = False) -> Contacts:
        """Déplace le chat et les objets, puis résout toutes les collisions."""
        contacts = Contacts()

        self._pousser_objets()
        self._faire_tomber_objets()

        bas_precedent = self.chat.bottom
        self.moteur.update()                       # murs durs + gravité
        self._garder_dans_le_niveau()
        plateforme = self._poser_sur_plateforme(bas_precedent, descendre)
        self._agripper_le_rebord(descendre)

        contacts.sur_plateforme = plateforme is not None
        contacts.au_sol = self.est_au_sol()
        contacts.atterrissage = contacts.au_sol and not self._etait_au_sol

        self._suivre_la_chute(contacts, plateforme)
        self._etait_au_sol = contacts.au_sol

        contacts.hors_niveau = self.chat.center_y < self.bas_du_niveau
        contacts.zones = self._toucher(self.zones)
        self._verifier_les_mortels(contacts)

        if contacts.hors_niveau and not contacts.mort:
            contacts.mort = "le vide"
        return contacts

    def _garder_dans_le_niveau(self) -> None:
        """Le chat ne sort jamais du niveau par la gauche ou par la droite."""
        if self.chat.left < 0:
            self.chat.left = 0
            self.chat.change_x = 0
        if self.largeur_niveau is not None and self.chat.right > self.largeur_niveau:
            self.chat.right = self.largeur_niveau
            self.chat.change_x = 0

    # -- plateformes traversables ---------------------------------------
    def _poser_sur_plateforme(self, bas_precedent: float, descendre: bool):
        """Arrête la chute du chat sur une plateforme traversable.

        Trois conditions, toutes nécessaires :

        * le chat descend (``change_y <= 0``) ;
        * il ne demande pas à passer au travers (touche bas) ;
        * il était **au-dessus** de la plateforme à l'image précédente, sinon
          on serait téléporté sur le toit d'une plateforme traversée en sautant.
        """
        if descendre or self.chat.change_y > 0:
            return None

        for liste in self.plateformes:
            for plateforme in arcade.check_for_collision_with_list(self.chat, liste):
                if bas_precedent >= plateforme.top - TOLERANCE_ATTERRISSAGE:
                    self.chat.bottom = plateforme.top
                    self.chat.change_y = 0
                    return plateforme
        return None

    def _sol_sous_le_centre(self) -> bool:
        """Y a-t-il du sol sous le *centre* du chat, et pas juste sous un bord ?

        ``est_au_sol()`` est volontairement permissif (on peut sauter depuis
        l'extrême bord). Ici on veut le contraire : savoir si le chat tient
        vraiment debout, pour qu'il ne s'agrippe pas en flottant dans le vide.
        """
        self._sonde.center_x = self.chat.center_x
        self._sonde.center_y = self.chat.bottom - SONDE_CENTRE / 2

        for listes in (self.murs, self.plateformes, self.poussables):
            for liste in listes:
                if arcade.check_for_collision_with_list(self._sonde, liste):
                    return True
        return False

    # -- réflexe : s'agripper au rebord ----------------------------------
    def _agripper_le_rebord(self, descendre: bool) -> None:
        """Le chat s'accroche par réflexe : il ne tombe jamais en marchant.

        Pour tomber, il faut sauter... ou désactiver le réflexe dans le niveau.
        """
        if not getattr(self.chat, "reflexe_agrippe", False):
            if self._sol_sous_le_centre():
                self._derniere_position_sure = (self.chat.center_x, self.chat.center_y)
            return

        quitte_le_sol_en_marchant = (
            self._etait_au_sol and self.chat.change_y <= 0 and not descendre
        )
        if quitte_le_sol_en_marchant and not self.est_au_sol():
            # Il glissait dans le vide : on le remet sur le rebord.
            self.chat.center_x, self.chat.center_y = self._derniere_position_sure
            self.chat.change_x = 0
            self.chat.change_y = 0
        elif self._sol_sous_le_centre():
            self._derniere_position_sure = (self.chat.center_x, self.chat.center_y)

    # -- chutes -----------------------------------------------------------
    def _suivre_la_chute(self, contacts: Contacts, plateforme) -> None:
        """Mesure la hauteur de chute et décide si elle fait griller une vie."""
        if contacts.au_sol:
            if contacts.atterrissage:
                contacts.hauteur_chute = max(
                    0.0, self._altitude_depart_chute - self.chat.center_y
                )
                if self._chute_fatale(contacts.hauteur_chute):
                    contacts.mort = "la chute"
            self._altitude_depart_chute = self.chat.center_y
        else:
            # Tant qu'il monte, le point de départ de la chute remonte avec lui.
            self._altitude_depart_chute = max(
                self._altitude_depart_chute, self.chat.center_y
            )

    def _chute_fatale(self, hauteur: float) -> bool:
        if self._amorti_par_un_objet():
            return False                      # un pouf en dessous, tout va bien
        if getattr(self.chat, "reflexe_pattes", False):
            return hauteur > C.CHUTE_MORTELLE_AVEC_PATTES
        return hauteur > C.CHUTE_MORTELLE

    def _amorti_par_un_objet(self) -> bool:
        """Y a-t-il un objet amortissant (un pouf) juste sous le chat ?"""
        self.chat.center_y -= SONDE_SOL
        objets = self._toucher(self.poussables)
        self.chat.center_y += SONDE_SOL
        return any(getattr(objet, "amortit", False) for objet in objets)

    # -- éléments mortels --------------------------------------------------
    def _verifier_les_mortels(self, contacts: Contacts) -> None:
        touches = self._toucher(self.mortels)
        if not touches:
            return

        if getattr(self.chat, "reflexe_moustaches", False):
            # Les moustaches détectent l'obstacle : le chat l'esquive et recule.
            contacts.esquive = True
            self.chat.center_x -= self.chat.change_x * 2
            self.chat.change_x = 0
            return

        contacts.mortels = touches
        contacts.mort = getattr(touches[0], "cause_de_mort", "les pointes")

    # -- objets poussables --------------------------------------------------
    def _pousser_objets(self) -> None:
        """Le chat pousse un pouf en marchant dedans (déplacement horizontal).

        On pousse AVANT le déplacement du chat : si l'objet ne peut pas bouger,
        le moteur d'arcade bloquera ensuite le chat contre lui, naturellement.
        """
        if self.chat.change_x == 0 or not self.poussables:
            return

        pas = max(-C.VITESSE_POUSSEE, min(C.VITESSE_POUSSEE, self.chat.change_x))

        self.chat.center_x += self.chat.change_x   # où le chat veut aller
        objets = self._toucher(self.poussables)
        self.chat.center_x -= self.chat.change_x

        for objet in objets:
            self._deplacer_objet(objet, pas)

    def _deplacer_objet(self, objet, pas: float, profondeur: int = 0) -> bool:
        """Déplace un objet, et la pile d'objets qu'il pousse à son tour.

        Retourne False si ça coince : dans ce cas rien n'a bougé. La pile est
        limitée (``PILE_POUSSABLE_MAX``), sinon le chat pousserait tout le salon.
        """
        objet.center_x += pas

        if self._contre_un_mur(objet):
            objet.center_x -= pas
            return False

        voisins = self._objets_en_contact(objet)
        if voisins and profondeur >= C.PILE_POUSSABLE_MAX - 1:
            objet.center_x -= pas
            return False

        for voisin in voisins:
            if not self._deplacer_objet(voisin, pas, profondeur + 1):
                objet.center_x -= pas
                return False
        return True

    def _contre_un_mur(self, objet) -> bool:
        for liste in self.murs:
            if arcade.check_for_collision_with_list(objet, liste):
                return True
        return False

    def _objets_en_contact(self, objet):
        voisins = []
        for liste in self.poussables:
            for autre in arcade.check_for_collision_with_list(objet, liste):
                if autre is not objet:
                    voisins.append(autre)
        return voisins

    def _faire_tomber_objets(self) -> None:
        """Gravité des objets poussables : ils tombent et se posent."""
        for liste in self.poussables:
            for objet in liste:
                objet.change_y -= self.gravite
                objet.change_y = max(objet.change_y, -C.VITESSE_CHUTE_MAX)
                objet.center_y += objet.change_y

                support = self._support_sous(objet)
                if support is not None:
                    objet.bottom = support
                    objet.change_y = 0
                elif objet.top < self.bas_du_niveau:
                    objet.remove_from_sprite_lists()   # sorti du niveau

    def _support_sous(self, objet):
        """Retourne l'altitude du dessus du premier support touché, sinon None."""
        for liste in self.murs + self.poussables:
            for autre in arcade.check_for_collision_with_list(objet, liste):
                if autre is objet:
                    continue
                if objet.change_y <= 0 and objet.center_y > autre.center_y:
                    return autre.top
        for liste in self.plateformes:
            for plateforme in arcade.check_for_collision_with_list(objet, liste):
                if objet.change_y <= 0 and objet.bottom < plateforme.top <= objet.center_y:
                    return plateforme.top
        return None

    # -- utilitaire ---------------------------------------------------------
    def _toucher(self, listes):
        touches = []
        for liste in listes:
            touches.extend(arcade.check_for_collision_with_list(self.chat, liste))
        return touches

    # ------------------------------------------------------------------
    def dessiner_debug(self) -> None:
        """Affiche les boîtes de collision (touche F1 en jeu)."""
        for liste in self.murs:
            liste.draw_hit_boxes(arcade.color.LIME)
        for liste in self.plateformes:
            liste.draw_hit_boxes(arcade.color.YELLOW)
        for liste in self.mortels:
            liste.draw_hit_boxes(arcade.color.RED)
        for liste in self.poussables:
            liste.draw_hit_boxes(arcade.color.ORANGE)
        for liste in self.zones:
            liste.draw_hit_boxes(arcade.color.CYAN)
