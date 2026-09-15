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

    def on_show_view(self) -> None:
        self.window.background_color = C.COULEUR_FOND

    # ------------------------------------------------------------------
    def on_update(self, delta_time: float) -> None:
        au_sol = self.collisions.est_au_sol()
        self.chat.calculer_deplacement(delta_time, au_sol)
        contacts = self.collisions.mettre_a_jour(descendre=self.chat.veut_descendre)

        if contacts.esquive:
            self.afficher("Les moustaches ont senti le danger !")

        if not contacts.vivant:
            self.griller_une_vie(contacts.mort)

        self.minuteur_message = max(0.0, self.minuteur_message - delta_time)

    def griller_une_vie(self, cause: str) -> None:
        """Le chat change de vie : c'est l'objectif du niveau, pas un échec."""
        self.vies -= 1
        self.afficher(f"Une vie de moins, emportée par {cause}. Il en reste {self.vies}.")

        # TODO (vies.py) : enregistrer la cicatrice et passer au niveau suivant.
        self.chat.replacer_au_depart()

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
            f"{self.niveau.titre}     Vies : {self.vies}",
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
        elif touche in C.TOUCHES_RECOMMENCER:
            self.charger_niveau(self.numero_niveau)
        elif touche in C.TOUCHES_DEBUG:
            self.debug = not self.debug
        elif touche in C.TOUCHES_PAUSE:
            arcade.exit()

    def on_key_release(self, touche: int, modificateurs: int) -> None:
        if touche in C.TOUCHES_GAUCHE:
            self.chat.veut_gauche = False
        elif touche in C.TOUCHES_DROITE:
            self.chat.veut_droite = False
        elif touche in C.TOUCHES_BAS:
            self.chat.veut_descendre = False

        if touche in C.TOUCHES_SAUT:
            self.chat.relacher_saut()
