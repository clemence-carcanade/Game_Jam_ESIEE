"""Sept Vies — point d'entrée.

    python main.py            le menu, puis le niveau 1
    python main.py 3          directement le niveau 3 (pratique en test)

Ce fichier ne contient aucune logique de jeu : il ouvre la fenêtre et affiche
la première vue. Le moteur est dans le paquet ``game/``.
"""

import sys

import arcade

from game import constantes as C
from game.jeu import VueJeu
from views.menu import MenuView


def main() -> None:
    fenetre = arcade.Window(
        C.LARGEUR_FENETRE,
        C.HAUTEUR_FENETRE,
        C.TITRE_FENETRE,
        update_rate=1 / C.IMAGES_PAR_SECONDE,
        center_window=True,
    )

    # Un numéro de niveau en argument saute le menu et lance la partie.
    if len(sys.argv) > 1:
        fenetre.show_view(VueJeu(int(sys.argv[1])))
    else:
        fenetre.show_view(MenuView())

    arcade.run()


if __name__ == "__main__":
    main()
