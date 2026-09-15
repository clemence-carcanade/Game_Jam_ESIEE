import arcade
import settings
from views.menu import MenuView


def main():
    window = arcade.Window(
        settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, settings.SCREEN_TITLE
    )
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()