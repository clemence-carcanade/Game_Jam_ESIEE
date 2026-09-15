import arcade
import arcade.gui


class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()

    def on_show_view(self):
        self.manager.enable()
        arcade.set_background_color(arcade.color.WOOD_BROWN)

        self.v_box = arcade.gui.UIBoxLayout(space_between=15)

        title_label = arcade.gui.UILabel(
            text="MON JEU DE PLATEFORME",
            font_size=28,
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
            # Le moteur de jeu vit dans game/ (voir README) ; l'ancien
            # GameView de main.py a ete remplace par VueJeu.
            from game.jeu import VueJeu

            self.window.show_view(VueJeu(1))