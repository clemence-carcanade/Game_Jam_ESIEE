import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Jeu de base - Arcade"

GRAVITY = 0.5
PLAYER_JUMP_SPEED = 10
PLAYER_MOVEMENT_SPEED = 5

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Fond blanc
        arcade.set_background_color(arcade.color.WHITE)

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

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.Q, arcade.key.D):
            self.player_change_x = 0


def main():
    window = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()