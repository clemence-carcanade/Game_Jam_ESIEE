"""Sept Vies -- point d'entree.

    python main.py        le menu, puis le jeu
    python main.py 3      directement le niveau 3 (debug)
"""

import sys

import arcade

from game import constantes as C
from game.jeu import VueJeu


def main() -> None:
    fenetre = arcade.Window(
        C.LARGEUR_FENETRE,
        C.HAUTEUR_FENETRE,
        C.TITRE_FENETRE,
        update_rate=1 / C.IMAGES_PAR_SECONDE,
        center_window=True,
    )

    if len(sys.argv) > 1:
        fenetre.show_view(VueJeu(int(sys.argv[1])))
    else:
        from views.menu import MenuView
        fenetre.show_view(MenuView())

    arcade.run()


if __name__ == "__main__":
    main()
