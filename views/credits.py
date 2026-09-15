import arcade
import settings


class CreditsView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BROWN)

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            "CRÉDITS",
            settings.SCREEN_WIDTH / 2,
            settings.SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            font_size=32,
            anchor_x="center",
            bold=True,
        )

        arcade.draw_text(
            "Jeu créé pour la Game Jam ESIEE",
            settings.SCREEN_WIDTH / 2,
            settings.SCREEN_HEIGHT / 2,
            arcade.color.LIGHT_GRAY,
            font_size=18,
            anchor_x="center",
        )

        arcade.draw_text(
            "Appuie sur ÉCHAP pour revenir au menu",
            settings.SCREEN_WIDTH / 2,
            80,
            arcade.color.GRAY,
            font_size=14,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            from views.menu import MenuView

            self.window.show_view(MenuView())