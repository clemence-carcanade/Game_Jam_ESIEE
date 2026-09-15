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
            text_color=arcade.color.WHITE,
        )
        self.v_box.add(title_label.with_padding(bottom=30))

        play_button = arcade.gui.UIFlatButton(text="PLAY", width=200, height=50)
        self.v_box.add(play_button)

        @play_button.event("on_click")
        def on_click_play(event):
            from views.game import GameView

            self.manager.disable()
            self.window.show_view(GameView())

        settings_button = arcade.gui.UIFlatButton(
            text="SETTINGS", width=200, height=50
        )
        self.v_box.add(settings_button)

        @settings_button.event("on_click")
        def on_click_settings(event):
            from views.settings import SettingsView

            self.manager.disable()
            self.window.show_view(SettingsView())

        credits_button = arcade.gui.UIFlatButton(
            text="CREDITS", width=200, height=50
        )
        self.v_box.add(credits_button)

        @credits_button.event("on_click")
        def on_click_credits(event):
            from views.credits import CreditsView

            self.manager.disable()
            self.window.show_view(CreditsView())

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
        self.manager.draw()