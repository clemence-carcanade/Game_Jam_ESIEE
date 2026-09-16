import os
import arcade
import arcade.gui
import settings
import pyglet
from PIL import Image


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

        # LOGO
        texture_logo = arcade.load_texture("assets/images/chatvamal_logo.png")
        self.logo = arcade.Sprite(texture_logo)
        self.logo.width = 400
        self.logo.height = int(
            400 * (texture_logo.height / texture_logo.width)
        )
        self.logo.center_x = settings.SCREEN_WIDTH / 2
        self.logo.center_y = settings.SCREEN_HEIGHT / 2 + 180

        # Charger la texture des boutons
        self.button_texture = arcade.load_texture("assets/images/buttons.png")

        # --- CURSEUR PERSONNALISÉ ---
        cursor_path = "assets/images/paw_cursor.png"
        if os.path.exists(cursor_path):
            TARGET_WIDTH, TARGET_HEIGHT = 32, 32
            pil_image = Image.open(cursor_path).resize(
                (TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS
            )
            raw_data = pil_image.tobytes()
            cursor_image = pyglet.image.ImageData(
                pil_image.width,
                pil_image.height,
                "RGBA",
                raw_data,
                pitch=-pil_image.width * 4,
            )
            self.custom_cursor = pyglet.window.ImageMouseCursor(
                cursor_image, 0, cursor_image.height
            )
        else:
            self.custom_cursor = None

        # --- ANIMATION DU CHAT (EN BAS À DROITE) ---
        # --- ANIMATION DU CHAT (EN BAS À DROITE) ---
        self.cat_textures = []
        self.current_cat_frame = 0
        self.cat_anim_timer = 0.0
        self.cat_frame_duration = 0.15

        cat_sheet_path = "assets/images/chat.png"
        if os.path.exists(cat_sheet_path):
            sprite_w, sprite_h = 32, 32
            # 1. On charge la planche complète
            full_sheet = arcade.load_texture(cat_sheet_path)
            
            # En Arcade, l'origine Y=0 d'une texture est en bas
            # La dernière ligne de pixels tout en bas est donc à y=0
            y_position = 0

            # 2. On découpe les 4 frames du bas avec .crop()
            for col in range(4):
                x_position = col * sprite_w
                texture = full_sheet.crop(x_position, y_position, sprite_w, sprite_h)
                self.cat_textures.append(texture)

            # Création du sprite
            self.cat_sprite = arcade.Sprite()
            self.cat_sprite.texture = self.cat_textures[0]
            self.cat_sprite.scale = 6

            self.cat_sprite.center_x = settings.SCREEN_WIDTH - 230
            self.cat_sprite.center_y = 220
        else:
            self.cat_sprite = None

    def create_custom_button(self, text, width, height, y_offset=-8):
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

        if self.custom_cursor:
            self.window.set_mouse_cursor(self.custom_cursor)

        self.v_box = arcade.gui.UIBoxLayout(space_between=5)

        button_width = 200
        button_height = int(
            button_width * (self.button_texture.height / self.button_texture.width)
        )

        OFFSET_Y = -20

        # --- Boutons ---
        play_button = self.create_custom_button("PLAY", button_width, button_height, y_offset=OFFSET_Y)
        self.v_box.add(play_button)

        @play_button.event("on_click")
        def on_click_play(event):
            from game.jeu import VueJeu
            self.manager.disable()
            self.window.show_view(VueJeu(1))

        settings_button = self.create_custom_button("SETTINGS", button_width, button_height, y_offset=OFFSET_Y)
        self.v_box.add(settings_button)

        @settings_button.event("on_click")
        def on_click_settings(event):
            from views.settings import SettingsView
            self.manager.disable()
            self.window.show_view(SettingsView())

        credits_button = self.create_custom_button("CREDITS", button_width, button_height, y_offset=OFFSET_Y)
        self.v_box.add(credits_button)

        @credits_button.event("on_click")
        def on_click_credits(event):
            from views.credits import CreditsView
            self.manager.disable()
            self.window.show_view(CreditsView())

        exit_button = self.create_custom_button("EXIT", button_width, button_height, y_offset=OFFSET_Y)
        self.v_box.add(exit_button)

        @exit_button.event("on_click")
        def on_click_exit(event):
            arcade.exit()

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y", align_y=-60)
        self.manager.add(anchor)

    def on_update(self, delta_time: float):
        # Mise à jour de l'animation du chat
        if self.cat_sprite and self.cat_textures:
            self.cat_anim_timer += delta_time
            if self.cat_anim_timer >= self.cat_frame_duration:
                self.cat_anim_timer = 0.0
                self.current_cat_frame = (self.current_cat_frame + 1) % len(self.cat_textures)
                self.cat_sprite.texture = self.cat_textures[self.current_cat_frame]

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        arcade.draw_sprite(self.background)
        arcade.draw_sprite(self.logo)

        # Dessin du chat animé
        if self.cat_sprite:
            arcade.draw_sprite(self.cat_sprite)

        self.manager.draw()