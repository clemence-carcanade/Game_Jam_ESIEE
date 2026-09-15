import sys
import arcade
import pyglet

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

    # Découpage du 4e curseur marron sur la 3e ligne (x=48, y=32, w=16, h=16)
    full_image = pyglet.image.load("assets/UI/small_cursors_100_.png")
    cursor_img = full_image.get_region(x=48, y=32, width=16, height=16)
    fenetre.set_mouse_cursor(pyglet.window.ImageMouseCursor(cursor_img, 0, 16))

    # Un numéro de niveau en argument saute le menu et lance la partie.
    if len(sys.argv) > 1:
        fenetre.show_view(VueJeu(int(sys.argv[1])))
    else:
        fenetre.show_view(MenuView())

    arcade.run()


if __name__ == "__main__":
    main()