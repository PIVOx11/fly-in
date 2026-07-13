import arcade
from Graph import Drone, Connection, Zone, Graph


class Display(arcade.Window):
    def __init__(self, graph: Graph = None, sim_data= None):

        super().__init__(resizable=True, title="Fly-in | by: blidriss")

        self.background_color = arcade.color.AMAZON
        self.graph = graph
        self.sim_data = sim_data
        self.auto_scale_x = 0
        self.auto_scale_y = 0
        self.min_x = min(zone.x for zone in graph.zones.values())
        self.max_x = max(zone.x for zone in graph.zones.values())
        self.min_y = min(zone.y for zone in graph.zones.values())
        self.max_y = max(zone.y for zone in graph.zones.values())
        self.margin = 160

    def get_cordonate(self, x: int, y: int):
        usable_width = self.width - self.margin
        usable_height = self.height - self.margin

        dx = max(self.max_x - self.min_x, 1)
        dy = max(self.max_y - self.min_y, 1)

        scale = min(usable_width / dx, usable_height / dy)

        start_x = (self.width - dx * scale) / 2
        start_y = (self.height - dy * scale) / 2

        screen_x = start_x + (x - self.min_x) * scale
        screen_y = start_y + (y - self.min_y) * scale

        return screen_x, screen_y

    def on_draw(self):
        self.clear()

        self.auto_scale_x = (self.width) / max(self.max_x - self.min_x, 1)
        self.auto_scale_y = (self.height) / max(self.max_y - self.min_y, 1)

        for zone in self.graph.zones.values():
            z_x = zone.x
            z_y = zone.y

            x, y = self.get_cordonate(z_x, z_y)
            arcade.draw_circle_filled(x, y, radius=30, color=(255, 0, 0))

