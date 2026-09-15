"""La vue principale : boucle de jeu, dessin, clavier.

Volontairement minimale pour l'instant : elle sert à faire tourner et à tester
le moteur de collisions. Le HUD définitif ira dans ``ui.py``, le compteur de
vies et les cicatrices dans ``vies.py``, les maîtres dans ``maitre.py`` — ce
fichier appellera simplement ces modules quand ils existeront.

Ordre d'une image :

    1. clavier     -> intentions du chat
    2. chat        -> vitesses (calculer_deplacement)
    3. collisions  -> déplacement réel, murs, plateformes, mortels, poussables
    4. jeu         -> vies, progression, dessin
"""

import arcade

from game import constantes as C
from game import niveau as module_niveau
from game.chat import Chat
from game.collisions import MoteurCollisions

#: distance a laquelle le chat peut attraper un objet devant lui
PORTEE_ACTION = 14.0


class VueJeu(arcade.View):
    def __init__(self, numero_niveau: int = 1):
        super().__init__()
        self.numero_niveau = numero_niveau
        self.vies = C.VIES_DEPART
        self.debug = False
        self.message = ""
        self.minuteur_message = 0.0

        self.niveau = None
        self.chat = None
        self.collisions = None
        self.pause_mort = 0.0        # temps d'affichage du chat allonge
        self.rejouer = False         # au niveau 7, mourir fait recommencer
        self.gamelle = None          # la zone du piege a armer
        self.sortie = None           # niveau 7 : la ou il faut arriver vivant
        self.termine = False         # le jeu est fini
        self.charger_niveau(numero_niveau)

    # ------------------------------------------------------------------
    def charger_niveau(self, numero: int) -> None:
        self.numero_niveau = numero
        self.niveau = module_niveau.charger(numero)

        x, y = self.niveau.depart_chat
        self.chat = Chat(x, y)

        # Les métadonnées du niveau peuvent couper un réflexe dès le départ.
        for reflexe in self.niveau.reflexes_coupes:
            setattr(self.chat, f"reflexe_{reflexe}", False)

        self.collisions = MoteurCollisions(
            self.chat,
            murs=self.niveau.murs,
            plateformes=self.niveau.plateformes,
            mortels=self.niveau.mortels,
            poussables=self.niveau.poussables,
            zones=self.niveau.zones,
            largeur_niveau=self.niveau.largeur,
        )

        self.gamelle = self.niveau.trouver_zone("gamelle")
        self.sortie = self.niveau.trouver_zone("sortie")
        if self.niveau.aide:
            self.afficher(self.niveau.aide)

    def on_show_view(self) -> None:
        self.window.background_color = C.COULEUR_FOND

    # ------------------------------------------------------------------
    def on_update(self, delta_time: float) -> None:
        self.minuteur_message = max(0.0, self.minuteur_message - delta_time)

        # TODO (vies.py) : cette pause et l'enchainement des niveaux
        # appartiennent au systeme de vies. Ici, juste de quoi voir l'animation.
        if self.pause_mort > 0:
            self.pause_mort -= delta_time
            self.chat.mettre_a_jour_animation(delta_time)
            if self.pause_mort <= 0:
                if getattr(self, "rejouer", False):
                    self.charger_niveau(self.numero_niveau)   # niveau 7 : on recommence
                else:
                    self.niveau_suivant()
                self.chat.vivant = True
            return

        au_sol = self.collisions.est_au_sol()
        self.chat.calculer_deplacement(delta_time, au_sol)
        contacts = self.collisions.mettre_a_jour(descendre=self.chat.veut_descendre)

        self._surfaces_glissantes(contacts)
        self._remplir_la_gamelle()
        self._sortir_du_sac()

        if contacts.atterrissage:
            self.chat.signaler_atterrissage()
        if contacts.esquive:
            self.afficher("Les moustaches ont senti le danger !")

        if not contacts.vivant:
            self.griller_une_vie(contacts.mort)

        if self.sortie is not None and arcade.check_for_collision(self.chat, self.sortie):
            self.gagner()

        self.chat.mettre_a_jour_animation(delta_time)

    # ------------------------------------------------------------------
    # Le salon : verre glissant, gamelle, sac de croquettes
    # ------------------------------------------------------------------
    def _surfaces_glissantes(self, contacts) -> None:
        """La table du salon n'est pas en verre, c'est un film plastique."""
        self.chat.sur_surface_glissante = any(
            getattr(zone, "role", "") == "verre" for zone in contacts.zones
        )

    def _remplir_la_gamelle(self) -> None:
        """Un objet renverse dans la gamelle y deverse son contenu."""
        if self.gamelle is None or self.gamelle.remplie:
            return

        renverse = arcade.check_for_collision_with_list(
            self.gamelle, self.niveau.poussables
        )
        if renverse:
            self.gamelle.remplie = True
            self.gamelle.color = C.COULEUR_POUSSABLE
            # le sac se vide entierement dans la gamelle : on le retire, sinon
            # il resterait plante devant et empecherait le chat de manger
            for objet in renverse:
                objet.remove_from_sprite_lists()
            self.afficher(self.niveau.message_piege
                          or "Le sac se renverse dans la gamelle. Les croquettes du fond, celles qui sentent.")

    def _sortir_du_sac(self) -> None:
        """Le chat coince dans le sac s'arrete des qu'il percute quelque chose."""
        if self.chat.dans_le_sac and abs(self.chat.change_x) < 0.5:
            self.chat.liberer_du_sac()
            self.afficher("Le chat percute le mur. Il se degage. Toujours vivant.")

    def manger(self) -> None:
        """Le seul vrai danger du salon."""
        if self.gamelle is None:
            return
        if not arcade.check_for_collision(self.chat, self.gamelle):
            return

        if self.gamelle.remplie:
            self.griller_une_vie("les croquettes avariees")
        else:
            self.afficher("Les memes croquettes que tous les soirs. Meme pas de quoi s etouffer.")

    def se_coincer_dans_le_sac(self) -> bool:
        """Faux piege : le chat met la tete dans le sac et fonce dans le decor.

        On regarde **devant** le chat : un objet solide ne le chevauche jamais,
        le moteur les a separes. Sans ce decalage, E ne marcherait jamais.
        """
        depart = self.chat.center_x
        self.chat.center_x += self.chat.regarde * PORTEE_ACTION
        touche = arcade.check_for_collision_with_list(self.chat, self.niveau.poussables)
        self.chat.center_x = depart

        if not touche:
            return False
        self.chat.coincer_dans_le_sac()
        self.afficher("Le chat a la tete dans le sac. Il ne voit plus rien.")
        return True

    def griller_une_vie(self, cause: str) -> None:
        """Le chat change de vie.

        Dans les six premiers niveaux, c'est l'objectif : la vie brulee fait
        passer au foyer suivant. Au septieme, le jeu s'inverse — le chat est
        enfin heureux, mourir devient l'echec et on recommence le niveau.
        """
        if self.termine:
            return

        self.chat.vivant = False
        self.chat.change_x = self.chat.change_y = 0
        self.pause_mort = 1.6

        if self.niveau.survivre:
            self.afficher(self.niveau.message_mort
                          or f"Pas comme ca. Pas maintenant. ({cause})")
            self.rejouer = True
            return

        self.vies -= 1
        self.rejouer = False
        self.afficher(self.niveau.message_mort
                      or f"Une vie de moins, emportee par {cause}. Il en reste {self.vies}.")

    def gagner(self) -> None:
        """Dernier niveau : le chat a tenu. C'est fini."""
        if self.termine:
            return
        self.termine = True
        self.afficher("Il est reste. Pour une fois, il est reste.")

    def niveau_suivant(self) -> None:
        if self.numero_niveau >= C.NOMBRE_NIVEAUX:
            self.termine = True
            self.afficher("Sept vies, sept maisons. Il ne lui en restait qu'une.")
            return
        self.charger_niveau(self.numero_niveau + 1)

    def afficher(self, texte: str) -> None:
        self.message = texte
        self.minuteur_message = 2.5

    # ------------------------------------------------------------------
    def on_draw(self) -> None:
        self.clear()
        self.niveau.dessiner()
        arcade.draw_sprite(self.chat)

        if self.debug:
            self.collisions.dessiner_debug()

        arcade.draw_text(
            f"{self.numero_niveau}/{C.NOMBRE_NIVEAUX}  {self.niveau.titre}     Vies : {self.vies}",
            16, C.HAUTEUR_FENETRE - 30, C.COULEUR_TEXTE, 16,
        )
        if self.niveau.aide:
            arcade.draw_text(
                self.niveau.aide, C.LARGEUR_FENETRE / 2, 16,
                C.COULEUR_TEXTE_FADE, 13, anchor_x="center",
            )
        if self.minuteur_message > 0:
            arcade.draw_text(
                self.message, C.LARGEUR_FENETRE / 2, C.HAUTEUR_FENETRE - 70,
                C.COULEUR_TEXTE, 18, anchor_x="center",
            )

    # ------------------------------------------------------------------
    def on_key_press(self, touche: int, modificateurs: int) -> None:
        if touche in C.TOUCHES_GAUCHE:
            self.chat.veut_gauche = True
        elif touche in C.TOUCHES_DROITE:
            self.chat.veut_droite = True
        elif touche in C.TOUCHES_BAS:
            self.chat.veut_descendre = True

        if touche in C.TOUCHES_SAUT:
            self.chat.demander_saut()
        elif touche in C.TOUCHES_ACTION:
            self.interagir()
        elif touche in C.TOUCHES_RECOMMENCER:
            self.charger_niveau(self.numero_niveau)
        elif touche in C.TOUCHES_DEBUG:
            self.debug = not self.debug
        elif touche in C.TOUCHES_PAUSE:
            arcade.exit()

    def interagir(self) -> None:
        """Touche E : le chat essaie quelque chose la ou il est.

        La gamelle passe avant le sac : une fois les croquettes renversees, le
        sac vide traine juste a cote, et ce serait rageant de rater le repas.
        """
        if self.chat.dans_le_sac:
            return
        if self.gamelle is not None and self.gamelle.remplie:
            if arcade.check_for_collision(self.chat, self.gamelle):
                self.manger()
                return
        if self.se_coincer_dans_le_sac():
            return
        self.manger()

    def on_key_release(self, touche: int, modificateurs: int) -> None:
        if touche in C.TOUCHES_GAUCHE:
            self.chat.veut_gauche = False
        elif touche in C.TOUCHES_DROITE:
            self.chat.veut_droite = False
        elif touche in C.TOUCHES_BAS:
            self.chat.veut_descendre = False

        if touche in C.TOUCHES_SAUT:
            self.chat.relacher_saut()
