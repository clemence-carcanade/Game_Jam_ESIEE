import os
import arcade
import arcade.gui
import settings


class MenuView(arcade.View):

    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()

        # Chargement sécurisé de la police
        font_path = "assets/fonts/8-bit Arcade In.ttf"
        if os.path.exists(font_path):
            arcade.load_font(font_path)
            self.font_name = "8-bit Arcade In"
        else:
            self.font_name = "Arial"

        # Image de fond
        texture_bg = arcade.load_texture("assets/images/background_menu.png")
        self.background = arcade.Sprite(texture_bg)
        self.background.center_x = settings.SCREEN_WIDTH / 2
        self.background.center_y = settings.SCREEN_HEIGHT / 2
        self.background.width = settings.SCREEN_WIDTH
        self.background.height = settings.SCREEN_HEIGHT

        # LOGO (Sprite indépendant du GUI)
        texture_logo = arcade.load_texture("assets/images/chatvamal_logo.png")
        self.logo = arcade.Sprite(texture_logo)
        self.logo.width = 400
        self.logo.height = int(
            400 * (texture_logo.height / texture_logo.width)
        )
        # Positionnement au centre X, et vers le haut de l'écran
        self.logo.center_x = settings.SCREEN_WIDTH / 2
        self.logo.center_y = settings.SCREEN_HEIGHT / 2 + 180

        # Charger la texture des boutons
        self.button_texture = arcade.load_texture("assets/images/buttons.png")

    def create_custom_button(self, text, width, height, y_offset=-8):
        """Crée un bouton avec le texte décalé vers le bas via un padding ou un décalage d'enfant."""
        custom_style = {
            "normal": arcade.gui.UITextureButton.UIStyle(
                font_name=self.font_name,
                font_size=26,
                font_color=arcade.color.WHITE,
            ),
            "hover": arcade.gui.UITextureButton.UIStyle(
                font_name=self.font_name,
                font_size=26,
                font_color=arcade.color.YELLOW,
            ),
            "press": arcade.gui.UITextureButton.UIStyle(
                font_name=self.font_name,
                font_size=26,
                font_color=arcade.color.GRAY,
            ),
        }

        button = arcade.gui.UITextureButton(
            text=text,
            texture=self.button_texture,
            width=width,
            height=height,
            style=custom_style,
        )

        for child in button.children:
            if isinstance(child, arcade.gui.UILabel):
                child.move(0, y_offset)

        return button

    def on_show_view(self):
        self.manager.enable()

        self.v_box = arcade.gui.UIBoxLayout(space_between=5)

        # Dimensions des boutons
        button_width = 200
        button_height = int(
            button_width * (self.button_texture.height / self.button_texture.width)
        )

        OFFSET_Y = -20

        # --- Bouton PLAY ---
        play_button = self.create_custom_button("PLAY", button_width, button_height, y_offset=OFFSET_Y)
        self.v_box.add(play_button)

        @play_button.event("on_click")
        def on_click_play(event):
            from game.jeu import VueJeu

            self.manager.disable()
            self.window.show_view(VueJeu(1))

        # --- Bouton SETTINGS ---
        settings_button = self.create_custom_button("SETTINGS", button_width, button_height, y_offset=OFFSET_Y)
        self.v_box.add(settings_button)

        @settings_button.event("on_click")
        def on_click_settings(event):
            from views.settings import SettingsView

            self.manager.disable()
            self.window.show_view(SettingsView())

        # --- Bouton CREDITS ---
        credits_button = self.create_custom_button("CREDITS", button_width, button_height, y_offset=OFFSET_Y)
        self.v_box.add(credits_button)

        @credits_button.event("on_click")
        def on_click_credits(event):
            from views.credits import CreditsView

            self.manager.disable()
            self.window.show_view(CreditsView())

        # --- Bouton EXIT ---
        exit_button = self.create_custom_button("EXIT", button_width, button_height, y_offset=OFFSET_Y)
        self.v_box.add(exit_button)

        @exit_button.event("on_click")
        def on_click_exit(event):
            arcade.exit()

        anchor = arcade.gui.UIAnchorLayout()
        # Repositionnement du bloc de boutons un peu plus bas sous le logo
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y", align_y=-60)
        self.manager.add(anchor)

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.background)
        arcade.draw_sprite(self.logo)  # Dessin du logo
        self.manager.draw()