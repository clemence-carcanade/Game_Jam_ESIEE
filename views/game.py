import arcade
import arcade.gui
import settings


class MenuView(arcade.View):

    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()

        # Répétition de la tuile sur tout l'écran
        self.background_list = arcade.SpriteList()
        texture = arcade.load_texture("assets/UI/Tile.png")

        tile_size = 32  # Ajuste la taille si tu souhaites agrandir/réduire les tuiles
        scale = tile_size / texture.width

        for x in range(0, settings.SCREEN_WIDTH + tile_size, tile_size):
            for y in range(0, settings.SCREEN_HEIGHT + tile_size, tile_size):
                tile = arcade.Sprite(texture, scale=scale)
                tile.center_x = x
                tile.center_y = y
                self.background_list.append(tile)

    def on_show_view(self):
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout(space_between=15)

        title_label = arcade.gui.UILabel(
            text="SEPT VIES",
            font_size=28,
            bold=True,
            text_color=arcade.color.WHITE,
        )
        self.v_box.add(title_label.with_padding(bottom=30))

        # --- Bouton PLAY ---
        play_button = arcade.gui.UIFlatButton(text="PLAY", width=200, height=50)
        self.v_box.add(play_button)

        @play_button.event("on_click")
        def on_click_play(event):
            from game.jeu import VueJeu

            self.manager.disable()
            self.window.show_view(VueJeu(1))

        # --- Bouton SETTINGS ---
        settings_button = arcade.gui.UIFlatButton(
            text="SETTINGS", width=200, height=50
        )
        self.v_box.add(settings_button)

        @settings_button.event("on_click")
        def on_click_settings(event):
            from views.settings import SettingsView

            self.manager.disable()
            self.window.show_view(SettingsView())

        # --- Bouton CREDITS ---
        credits_button = arcade.gui.UIFlatButton(
            text="CREDITS", width=200, height=50
        )
        self.v_box.add(credits_button)

        @credits_button.event("on_click")
        def on_click_credits(event):
            from views.credits import CreditsView

            self.manager.disable()
            self.window.show_view(CreditsView())

        # --- Bouton EXIT ---
        exit_button = arcade.gui.UIFlatButton(text="EXIT", width=200, height=50)
        self.v_box.add(exit_button)

        @exit_button.event("on_click")
        def on_click_exit(event):
            arcade.exit()

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.background_list.draw()
        self.manager.draw()