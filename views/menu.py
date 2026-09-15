import arcade
import settings


class MenuView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()

        # Titre du jeu
        arcade.draw_text(
            "MON JEU DE PLATEFORME",
            settings.SCREEN_WIDTH / 2,
            settings.SCREEN_HEIGHT - 150,
            arcade.color.BLACK,
            font_size=32,
            anchor_x="center",
            bold=True,
        )

        # Instruction
        arcade.draw_text(
            "Appuie sur ENTRÉE pour jouer",
            settings.SCREEN_WIDTH / 2,
            settings.SCREEN_HEIGHT / 2,
            arcade.color.DARK_GRAY,
            font_size=20,
            anchor_x="center",
        )

        # Contrôles
        arcade.draw_text(
            "Contrôles : Q (gauche), D (droite), ESPACE (saut)",
            settings.SCREEN_WIDTH / 2,
            100,
            arcade.color.GRAY,
            font_size=14,
            anchor_x="center",
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER:
            from main import GameView

            game_view = GameView()
            self.window.show_view(game_view)