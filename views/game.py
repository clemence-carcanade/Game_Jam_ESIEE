import arcade
import settings


class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.WHITE)

        self.player_x = 100
        self.player_y = 150
        self.player_change_x = 0
        self.player_change_y = 0
        self.player_width = 30
        self.player_height = 50

        self.ground_height = 50
        self.is_on_ground = True

    def on_draw(self):
        self.clear()

        arcade.draw_polygon_filled(
            [
                (0, 0),
                (settings.SCREEN_WIDTH, 0),
                (settings.SCREEN_WIDTH, self.ground_height),
                (0, self.ground_height),
            ],
            arcade.color.BLACK,
        )

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
            "ÉCHAP pour revenir au menu",
            10,
            settings.SCREEN_HEIGHT - 25,
            arcade.color.GRAY,
            font_size=12,
        )

    def on_update(self, delta_time):
        self.player_change_y -= settings.GRAVITY
        self.player_x += self.player_change_x
        self.player_y += self.player_change_y

        min_y = self.ground_height + self.player_height / 2
        if self.player_y <= min_y:
            self.player_y = min_y
            self.player_change_y = 0
            self.is_on_ground = True

        min_x = self.player_width / 2
        max_x = settings.SCREEN_WIDTH - self.player_width / 2
        if self.player_x < min_x:
            self.player_x = min_x
        elif self.player_x > max_x:
            self.player_x = max_x

    def on_key_press(self, key, modifiers):
        if key == arcade.key.Q:
            self.player_change_x = -settings.PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.player_change_x = settings.PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.SPACE and self.is_on_ground:
            self.player_change_y = settings.PLAYER_JUMP_SPEED
            self.is_on_ground = False
        elif key == arcade.key.ESCAPE:
            from views.menu import MenuView

            self.window.show_view(MenuView())

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.Q, arcade.key.D):
            self.player_change_x = 0