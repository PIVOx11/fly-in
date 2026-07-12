import arcade


class Fly(arcade.Window):
    def __init__(self):
        super().__init__(resizable=True, title="PIVOx")
        self.background_color = arcade.color.AMAZON

    def on_draw(self):
        self.clear()
        arcade.draw_circle_outline(center_x=100, center_y= 100 ,radius=50, color=(255,0,0))


window = Fly()

arcade.run()