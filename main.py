"""Sept Vies — point d'entrée.

    python main.py            lance le niveau 1
    python main.py 3          lance directement le niveau 3 (pratique en test)

Ce fichier ne contient aucune logique de jeu : il ouvre la fenêtre et affiche
la vue. Tout le reste est dans le paquet ``game/``.
"""

import sys

import arcade

from game import constantes as C
from game.jeu import VueJeu


def main() -> None:
    numero_niveau = int(sys.argv[1]) if len(sys.argv) > 1 else 1

    fenetre = arcade.Window(
        C.LARGEUR_FENETRE,
        C.HAUTEUR_FENETRE,
        C.TITRE_FENETRE,
        update_rate=1 / C.IMAGES_PAR_SECONDE,
        center_window=True,
    )
    fenetre.show_view(VueJeu(numero_niveau))
    arcade.run()


if __name__ == "__main__":
    main()
