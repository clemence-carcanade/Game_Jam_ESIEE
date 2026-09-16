"""Ecran des parametres : reglage du volume et rappel des commandes."""

import arcade

from game import audio as _audio
from game import constantes as C


class SettingsView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color((28, 26, 38))

    def _barre_volume(self):
        """Dessine la jauge de volume."""
        L = C.LARGEUR_FENETRE
        cx = L / 2
        y = C.HAUTEUR_FENETRE / 2 + 40
        larg = 400
        arcade.draw_text("VOLUME", cx, y + 40, arcade.color.WHITE, 22,
                         anchor_x="center", bold=True)
        # le rail
        arcade.draw_lrbt_rectangle_filled(cx - larg/2, cx + larg/2, y - 6, y + 6, (70, 66, 82))
        # le remplissage selon le volume
        rempli = larg * _audio.VOLUME
        arcade.draw_lrbt_rectangle_filled(cx - larg/2, cx - larg/2 + rempli, y - 6, y + 6,
                                          (200, 180, 120))
        # le curseur
        arcade.draw_circle_filled(cx - larg/2 + rempli, y, 12, (255, 240, 190))
        arcade.draw_text(f"{int(_audio.VOLUME * 100)} %", cx, y - 44,
                         arcade.color.LIGHT_GRAY, 18, anchor_x="center")
        arcade.draw_text("Fleches gauche / droite pour regler",
                         cx, y - 74, arcade.color.GRAY, 14, anchor_x="center")

    def on_draw(self):
        self.clear()
        cx = C.LARGEUR_FENETRE / 2
        arcade.draw_text("PARAMETRES", cx, C.HAUTEUR_FENETRE - 100,
                         arcade.color.WHITE, 34, anchor_x="center", bold=True)
        self._barre_volume()
        arcade.draw_text(
            "Commandes :  Q / D  deplacer     ESPACE  sauter     E  agir     S  descendre",
            cx, 140, arcade.color.LIGHT_GRAY, 15, anchor_x="center")
        arcade.draw_text("ECHAP pour revenir au menu",
                         cx, 90, arcade.color.GRAY, 14, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            _audio.regler_volume(_audio.VOLUME - 0.05)
        elif key == arcade.key.RIGHT:
            _audio.regler_volume(_audio.VOLUME + 0.05)
        elif key == arcade.key.ESCAPE:
            from views.menu import MenuView
            self.window.show_view(MenuView())
