import arcade
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Jeu de base - Arcade"

GRAVITY = 0.5
PLAYER_JUMP_SPEED = 10
PLAYER_MOVEMENT_SPEED = 5

NB_NIVEAUX = 7

# Dossier "musique" placé à côté de ce script, contenant une musique par niveau.
# Renomme tes fichiers (ou adapte cette liste) pour qu'ils correspondent.
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")
LEVEL_MUSIC_FILES = [
    os.path.join(MUSIC_DIR, f"lvl{i}.mp3") for i in range(1, NB_NIVEAUX + 1)
]


# ----------------------------------------------------------------------------
# Gestion de la musique
# ----------------------------------------------------------------------------
class MusicManager:
    """Charge les musiques (une par niveau), gère la lecture en boucle et le
    volume, partagé entre toutes les Views (menu, options, pause, jeu)."""

    def __init__(self, file_paths):
        self.volume = 0.5  # 0.0 -> 1.0
        self.player = None
        self.current_track_index = None
        self.tracks = []

        for path in file_paths:
            if os.path.exists(path):
                try:
                    self.tracks.append(arcade.Sound(path, streaming=True))
                except Exception as e:
                    print(f"Impossible de charger {path} : {e}")
                    self.tracks.append(None)
            else:
                print(f"Musique introuvable : {path}")
                self.tracks.append(None)

    def play_track(self, index):
        """Joue la musique du niveau `index` (0 = niveau 1). Ne relance pas
        la piste si elle est déjà en cours de lecture."""
        if index < 0 or index >= len(self.tracks):
            return

        if self.current_track_index == index and self.player is not None and self.player.playing:
            return  # déjà en train de jouer, on ne coupe pas le son

        if self.player is not None:
            try:
                self.player.pause()
            except Exception:
                pass
            self.player = None

        self.current_track_index = index
        sound = self.tracks[index]
        if sound is None:
            return  # fichier manquant : pas de musique, mais pas de crash
        self.player = sound.play(volume=self.volume, loop=True)

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        if self.player is not None:
            self.player.volume = self.volume

    def change_volume(self, delta):
        self.set_volume(self.volume + delta)


# ----------------------------------------------------------------------------
# Composants UI réutilisables : bouton et barre de volume
# ----------------------------------------------------------------------------
class Button:
    def __init__(self, center_x, center_y, width, height, text, font_size=16):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.text = text
        self.font_size = font_size

    @property
    def left(self):
        return self.center_x - self.width / 2

    @property
    def bottom(self):
        return self.center_y - self.height / 2

    def draw(self):
        arcade.draw_lbwh_rectangle_filled(
            self.left, self.bottom, self.width, self.height, arcade.color.DARK_SLATE_GRAY
        )
        arcade.draw_lbwh_rectangle_outline(
            self.left, self.bottom, self.width, self.height, arcade.color.WHITE, 2
        )
        arcade.draw_text(
            self.text,
            self.center_x,
            self.center_y,
            arcade.color.WHITE,
            font_size=self.font_size,
            anchor_x="center",
            anchor_y="center",
        )

    def contains(self, x, y):
        return (
            self.left <= x <= self.left + self.width
            and self.bottom <= y <= self.bottom + self.height
        )


class VolumeSlider:
    """Barre de volume cliquable/glissable à la souris."""

    def __init__(self, center_x, center_y, width, height, music_manager):
        self.center_x = center_x
        self.center_y = center_y
        self.width = width
        self.height = height
        self.music_manager = music_manager
        self.dragging = False

    @property
    def left(self):
        return self.center_x - self.width / 2

    @property
    def bottom(self):
        return self.center_y - self.height / 2

    def draw(self):
        arcade.draw_lbwh_rectangle_filled(
            self.left, self.bottom, self.width, self.height, arcade.color.DARK_GRAY
        )
        filled_width = self.width * self.music_manager.volume
        arcade.draw_lbwh_rectangle_filled(
            self.left, self.bottom, filled_width, self.height, arcade.color.GREEN
        )
        arcade.draw_lbwh_rectangle_outline(
            self.left, self.bottom, self.width, self.height, arcade.color.WHITE, 2
        )
        handle_x = self.left + filled_width
        arcade.draw_circle_filled(
            handle_x, self.center_y, self.height / 2 + 4, arcade.color.WHITE
        )
        arcade.draw_circle_outline(
            handle_x, self.center_y, self.height / 2 + 4, arcade.color.BLACK, 2
        )

    def contains(self, x, y):
        return (
            self.left - 8 <= x <= self.left + self.width + 8
            and self.bottom - 10 <= y <= self.bottom + self.height + 10
        )

    def set_volume_from_x(self, x):
        ratio = (x - self.left) / self.width
        self.music_manager.set_volume(ratio)

    def on_mouse_press(self, x, y):
        if self.contains(x, y):
            self.dragging = True
            self.set_volume_from_x(x)
            return True
        return False

    def on_mouse_drag(self, x, y):
        if self.dragging:
            self.set_volume_from_x(x)

    def on_mouse_release(self):
        self.dragging = False


# ----------------------------------------------------------------------------
# Menu principal
# ----------------------------------------------------------------------------
class MenuView(arcade.View):
    def __init__(self, music_manager):
        super().__init__()
        self.music_manager = music_manager

        self.play_button = Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 20, 220, 50, "Jouer")
        self.options_button = Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 50, 220, 50, "Options")

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        # Musique du menu = musique du niveau 1, tant qu'aucune autre ne joue déjà
        self.music_manager.play_track(0)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            SCREEN_TITLE,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 120,
            arcade.color.WHITE,
            font_size=36,
            anchor_x="center",
        )
        self.play_button.draw()
        self.options_button.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self._start_game()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.play_button.contains(x, y):
            self._start_game()
        elif self.options_button.contains(x, y):
            self.window.show_view(OptionsView(self.music_manager, return_view=self))

    def _start_game(self):
        game_view = GameView(self.music_manager, level=1)
        self.window.show_view(game_view)


# ----------------------------------------------------------------------------
# Options (accessible depuis le menu principal ET depuis la pause en jeu)
# ----------------------------------------------------------------------------
class OptionsView(arcade.View):
    def __init__(self, music_manager, return_view):
        super().__init__()
        self.music_manager = music_manager
        self.return_view = return_view  # vue vers laquelle revenir (menu ou pause)

        self.volume_slider = VolumeSlider(
            center_x=SCREEN_WIDTH / 2,
            center_y=SCREEN_HEIGHT / 2,
            width=320,
            height=20,
            music_manager=music_manager,
        )
        self.back_button = Button(SCREEN_WIDTH / 2, 80, 200, 45, "Retour")

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

    def on_draw(self):
        self.clear()
        arcade.draw_text(
            "Options",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 150,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
        )
        arcade.draw_text(
            "Audio",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 90,
            arcade.color.LIGHT_GRAY,
            font_size=18,
            anchor_x="center",
        )
        arcade.draw_text(
            "Volume musique (clique / glisse sur la barre)",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 45,
            arcade.color.LIGHT_GRAY,
            font_size=14,
            anchor_x="center",
        )

        self.volume_slider.draw()

        arcade.draw_text(
            f"{int(self.music_manager.volume * 100)}%",
            self.volume_slider.center_x,
            self.volume_slider.center_y - 40,
            arcade.color.WHITE,
            font_size=14,
            anchor_x="center",
        )

        self.back_button.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.return_view)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.back_button.contains(x, y):
            self.window.show_view(self.return_view)
            return
        self.volume_slider.on_mouse_press(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.volume_slider.on_mouse_drag(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.volume_slider.on_mouse_release()


# ----------------------------------------------------------------------------
# Menu pause (ouvert avec ECHAP pendant une partie)
# ----------------------------------------------------------------------------
class PauseView(arcade.View):
    def __init__(self, music_manager, game_view):
        super().__init__()
        self.music_manager = music_manager
        self.game_view = game_view  # instance conservée pour pouvoir reprendre

        self.resume_button = Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40, 240, 50, "Reprendre")
        self.options_button = Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30, 240, 50, "Options")
        self.menu_button = Button(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 100, 240, 50, "Menu principal")

    def on_draw(self):
        # On dessine le jeu figé en dessous, puis le menu pause par-dessus
        self.game_view.on_draw()

        arcade.draw_lbwh_rectangle_filled(
            0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 160)
        )
        arcade.draw_text(
            "Pause",
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT / 2 + 130,
            arcade.color.WHITE,
            font_size=32,
            anchor_x="center",
        )
        self.resume_button.draw()
        self.options_button.draw()
        self.menu_button.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.resume_button.contains(x, y):
            self.window.show_view(self.game_view)
        elif self.options_button.contains(x, y):
            self.window.show_view(OptionsView(self.music_manager, return_view=self))
        elif self.menu_button.contains(x, y):
            self.window.show_view(MenuView(self.music_manager))


# ----------------------------------------------------------------------------
# Jeu
# ----------------------------------------------------------------------------
class GameView(arcade.View):
    def __init__(self, music_manager, level=1):
        super().__init__()
        self.music_manager = music_manager
        self.level = level  # 1 à NB_NIVEAUX

        # Variables du joueur
        self.player_x = 100
        self.player_y = 150
        self.player_change_x = 0
        self.player_change_y = 0

        # Taille du joueur (rectangle)
        self.player_width = 30
        self.player_height = 50

        # Hauteur du sol
        self.ground_height = 50
        self.is_on_ground = True

    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)
        # Lance la musique correspondant au niveau (index = niveau - 1).
        self.music_manager.play_track(self.level - 1)

    # ------------------------------------------------------------------
    # Changement manuel de niveau (TEMPORAIRE, en attendant un vrai
    # système de progression). Change juste self.level et relance la
    # musique correspondante : aucun design de niveau requis.
    # ------------------------------------------------------------------
    def go_to_level(self, new_level):
        new_level = max(1, min(NB_NIVEAUX, new_level))
        if new_level == self.level:
            return
        self.level = new_level
        self.music_manager.play_track(self.level - 1)

    def next_level(self):
        self.go_to_level(self.level + 1)

    def previous_level(self):
        self.go_to_level(self.level - 1)

    def on_draw(self):
        self.clear()

        # Dessin du sol (rectangle noir)
        arcade.draw_polygon_filled(
            [
                (0, 0),
                (SCREEN_WIDTH, 0),
                (SCREEN_WIDTH, self.ground_height),
                (0, self.ground_height),
            ],
            arcade.color.BLACK,
        )

        # Dessin du personnage (rectangle bleu)
        arcade.draw_polygon_filled(
            [
                (
                    self.player_x - self.player_width / 2,
                    self.player_y - self.player_height / 2,
                ),
                (
                    self.player_x + self.player_width / 2,
                    self.player_y - self.player_height / 2,
                ),
                (
                    self.player_x + self.player_width / 2,
                    self.player_y + self.player_height / 2,
                ),
                (
                    self.player_x - self.player_width / 2,
                    self.player_y + self.player_height / 2,
                ),
            ],
            arcade.color.BLUE,
        )

        arcade.draw_text(
            f"Niveau {self.level} / {NB_NIVEAUX}   "
            f"(fleches HAUT/BAS: changer de niveau, ECHAP: pause)",
            10,
            SCREEN_HEIGHT - 20,
            arcade.color.GRAY,
            font_size=12,
        )

    def on_update(self, delta_time):
        # Application de la gravité
        self.player_change_y -= GRAVITY

        # Mise à jour des positions
        self.player_x += self.player_change_x
        self.player_y += self.player_change_y

        # Collision avec le sol
        min_y = self.ground_height + self.player_height / 2
        if self.player_y <= min_y:
            self.player_y = min_y
            self.player_change_y = 0
            self.is_on_ground = True

        # Limites de l'écran (gauche / droite)
        min_x = self.player_width / 2
        max_x = SCREEN_WIDTH - self.player_width / 2
        if self.player_x < min_x:
            self.player_x = min_x
        elif self.player_x > max_x:
            self.player_x = max_x

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            self.player_change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.player_change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.SPACE and self.is_on_ground:
            self.player_change_y = PLAYER_JUMP_SPEED
            self.is_on_ground = False
        elif key == arcade.key.ESCAPE:
            self.window.show_view(PauseView(self.music_manager, self))
        # --- Changement manuel de niveau (temporaire) ---
        elif key == arcade.key.UP:
            self.next_level()
        elif key == arcade.key.DOWN:
            self.previous_level()
        # Raccourcis directs 1 à 7 pour sauter directement à un niveau
        elif arcade.key.KEY_1 <= key <= arcade.key.KEY_1 + NB_NIVEAUX - 1:
            self.go_to_level(key - arcade.key.KEY_1 + 1)

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.Q, arcade.key.D):
            self.player_change_x = 0


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    music_manager = MusicManager(LEVEL_MUSIC_FILES)
    menu_view = MenuView(music_manager)
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()