import os
import arcade
import arcade.gui
import pyglet
from PIL import Image

from game import audio as _audio
from game import constantes as _S
from views.ui_logique import UIManagerLogique


class SettingsView(arcade.View):

    def __init__(self):
        super().__init__()
        self.manager = UIManagerLogique()

        # Le volume du jeu (de 0.0 à 1.0)
        self.volume = _audio.VOLUME
        self.is_dragging_slider = False  # Suivi du glissement à la souris

        # Chargement de la police 8-bit
        font_path = "assets/fonts/8-bit Arcade In.ttf"
        if os.path.exists(font_path):
            arcade.load_font(font_path)
            self.font_name = "8-bit Arcade In"
        else:
            self.font_name = "Arial"

        # Image de fond
        texture_bg = arcade.load_texture("assets/images/background_menu.png")
        self.background = arcade.Sprite(texture_bg)
        self.background.center_x = _S.LARGEUR_FENETRE / 2
        self.background.center_y = _S.HAUTEUR_FENETRE / 2
        self.background.width = _S.LARGEUR_FENETRE
        self.background.height = _S.HAUTEUR_FENETRE

        # Textures
        self.button_texture = arcade.load_texture("assets/images/buttons.png")
        self.close_texture = arcade.load_texture("assets/images/close_button.png")

        # Panneau en bois
        texture_panel = arcade.load_texture("assets/images/wood_panel.png")
        self.wood_panel = arcade.Sprite(texture_panel)
        self.wood_panel.scale = 0.8
        self.wood_panel.center_x = _S.LARGEUR_FENETRE / 2
        self.wood_panel.center_y = _S.HAUTEUR_FENETRE / 2 - 20

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
        self.cat_textures = []
        self.current_cat_frame = 0
        self.cat_anim_timer = 0.0
        self.cat_frame_duration = 0.15

        cat_sheet_path = "assets/images/chat.png"
        if os.path.exists(cat_sheet_path):
            sprite_w, sprite_h = 32, 32
            full_sheet = arcade.load_texture(cat_sheet_path)
            y_position = 0

            for col in range(4):
                x_position = col * sprite_w
                texture = full_sheet.crop(x_position, y_position, sprite_w, sprite_h)
                self.cat_textures.append(texture)

            self.cat_sprite = arcade.Sprite()
            self.cat_sprite.texture = self.cat_textures[0]
            self.cat_sprite.scale = 6
            self.cat_sprite.center_x = _S.LARGEUR_FENETRE - 230
            self.cat_sprite.center_y = 220
        else:
            self.cat_sprite = None

    def create_title_button(self, text, width, height, y_offset=-20):
        static_style = arcade.gui.UITextureButton.UIStyle(
            font_name=self.font_name,
            font_size=26,
            font_color=arcade.color.WHITE,
        )

        button_style = {
            "normal": static_style,
            "hover": static_style,
            "press": static_style,
        }

        button = arcade.gui.UITextureButton(
            text=text,
            texture=self.button_texture,
            width=width,
            height=height,
            style=button_style,
        )

        for child in button.children:
            if isinstance(child, arcade.gui.UILabel):
                child.move(0, y_offset)

        return button

    def create_close_button(self, size):
        close_btn = arcade.gui.UITextureButton(
            texture=self.close_texture,
            width=size,
            height=size,
        )

        @close_btn.event("on_click")
        def on_click_close(event):
            from views.menu import MenuView

            self.manager.disable()
            self.window.show_view(MenuView())

        return close_btn

    def _get_slider_dimensions(self):
        """Retourne la position et la taille de la barre."""
        cx = _S.LARGEUR_FENETRE / 2
        y = _S.HAUTEUR_FENETRE / 2 - 80
        
        # Réduis cette valeur pour raccourcir la barre (ex: 180 au lieu de 300)
        larg = 180 
        
        return cx, y, larg

    def _barre_volume(self):
        """Dessine la jauge de volume sous le titre VOLUME SONORE."""
        cx, y, larg = self._get_slider_dimensions()

        # Le rail
        arcade.draw_lrbt_rectangle_filled(
            cx - larg / 2, cx + larg / 2, y - 6, y + 6, (70, 66, 82)
        )

        # Remplissage visuel basé sur self.volume
        rempli = larg * self.volume

        arcade.draw_lrbt_rectangle_filled(
            cx - larg / 2, cx - larg / 2 + rempli, y - 6, y + 6, (200, 180, 120)
        )
        # Le curseur rond
        arcade.draw_circle_filled(
            cx - larg / 2 + rempli, y, 12, (255, 240, 190)
        )
        # Pourcentage du volume juste sous le rail
        arcade.draw_text(
            f"{int(self.volume * 100)} %",
            cx,
            y - 32,
            arcade.color.WHITE,
            18,
            anchor_x="center",
            font_name=self.font_name,
        )

    def _update_volume_from_mouse(self, x: float):
        """Calcule le volume en fonction de la position X de la souris."""
        cx, _, larg = self._get_slider_dimensions()
        left_bound = cx - larg / 2
        right_bound = cx + larg / 2

        clamped_x = max(left_bound, min(x, right_bound))
        self.volume = (clamped_x - left_bound) / larg

        _audio.regler_volume(self.volume)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            cx, slider_y, larg = self._get_slider_dimensions()
            left_bound = cx - larg / 2
            right_bound = cx + larg / 2

            if left_bound - 10 <= x <= right_bound + 10 and slider_y - 20 <= y <= slider_y + 20:
                self.is_dragging_slider = True
                self._update_volume_from_mouse(x)

    def on_mouse_drag(self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int):
        if self.is_dragging_slider:
            self._update_volume_from_mouse(x)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.is_dragging_slider = False

    def on_show_view(self):
        self.manager.enable()

        if self.custom_cursor:
            self.window.set_mouse_cursor(self.custom_cursor)

        button_width = 200
        button_height = int(
            button_width * (self.button_texture.height / self.button_texture.width)
        )

        close_scale = 0.8
        close_size = int(button_height * close_scale)

        title_button = self.create_title_button(
            "SETTINGS", button_width, button_height
        )
        close_button = self.create_close_button(size=close_size)

        row_layout = arcade.gui.UIBoxLayout(
            vertical=False, space_between=15, align="center"
        )
        row_layout.add(close_button)
        row_layout.add(title_button)

        settings_box = arcade.gui.UIBoxLayout(
            vertical=True, space_between=10, align="center"
        )

        label_title = arcade.gui.UILabel(
            text="COMMANDES :",
            font_name=self.font_name,
            font_size=24,
            text_color=arcade.color.WHITE,
            multiline=True,
            width=400,
            align="center",
        )

        label_controls = arcade.gui.UILabel(
            text="Q - D / FLECHES :\nSe deplacer\nESPACE : Sauter\nE : Interaction\nR : Respawn",
            font_name=self.font_name,
            font_size=18,
            text_color=arcade.color.WHITE,
            multiline=True,
            width=450,
            align="center",
        )

        label_sound = arcade.gui.UILabel(
            text="VOLUME SONORE :",
            font_name=self.font_name,
            font_size=24,
            text_color=arcade.color.WHITE,
            multiline=True,
            width=400,
            align="center",
        )

        settings_box.add(label_title)
        settings_box.add(label_controls)
        settings_box.add(label_sound)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(
            child=row_layout, anchor_x="center_x", anchor_y="center_y", align_y=200
        )
        # Position du bloc de texte ajustée plus haut
        anchor.add(
            child=settings_box,
            anchor_x="center_x",
            anchor_y="center_y",
            align_y=30,
        )

        self.manager.add(anchor)

    def on_update(self, delta_time: float):
        # Animation du chat
        if self.cat_sprite and self.cat_textures:
            self.cat_anim_timer += delta_time
            if self.cat_anim_timer >= self.cat_frame_duration:
                self.cat_anim_timer = 0.0
                self.current_cat_frame = (
                    self.current_cat_frame + 1
                ) % len(self.cat_textures)
                self.cat_sprite.texture = self.cat_textures[
                    self.current_cat_frame
                ]

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()

        # Dessin du fond et du panneau en bois
        arcade.draw_sprite(self.background)
        arcade.draw_sprite(self.wood_panel)

        # Dessin du chat animé
        if self.cat_sprite:
            arcade.draw_sprite(self.cat_sprite)

        # Dessin de l'interface GUI
        self.manager.draw()

        # Dessin du glisseur visuel
        self._barre_volume()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            from views.menu import MenuView

            self.window.show_view(MenuView())