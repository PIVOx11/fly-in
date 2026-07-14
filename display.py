import arcade
from Graph import Drone, Connection, Zone, Graph


class Display(arcade.Window):
    def __init__(self, graph: Graph = None, sim_data= None):

        super().__init__(resizable=True, title="Fly-in | by: blidriss")

        self.background_color = arcade.color.BLACK
        self.graph = graph
        self.sim_data = sim_data
        self.auto_scale_x = 0
        self.auto_scale_y = 0
        self.min_x = min(zone.x for zone in graph.zones.values())
        self.max_x = max(zone.x for zone in graph.zones.values())
        self.min_y = min(zone.y for zone in graph.zones.values())
        self.max_y = max(zone.y for zone in graph.zones.values())
        self.margin = 120
        self.d_image = arcade.load_texture("assert/drone.png")
        self.drone_x = 0
        self.drone_y = 0
        self.drone_progress = 0

    def get_cordonate(self, x: int, y: int):
        MAX_SCALE = 175
        usable_width = self.width - self.margin
        usable_height = self.height - self.margin

        dx = self.max_x - self.min_x
        dy = self.max_y - self.min_y

        scale_x = usable_width / max(dx, 1)
        scale_y = usable_height / max(dy, 1)

        scale = min(scale_x, scale_y, MAX_SCALE)

        start_x = (self.width - dx * scale) / 2
        start_y = (self.height - dy * scale) / 2 

        screen_x = start_x + x * scale
        screen_y = start_y + y * scale + 200

        return screen_x, screen_y, scale

    def on_update(self):
        if self.drone_progress < 1:
            self.drone_progress += 0.2
            self.drone_x, self.drone_y, self.scale = self.get_cordonate()
        else:

    def on_draw(self):
        self.clear()
        draw_conect = set()

        # draw connections
        for c in self.graph.zones.values():
            for con in c.connections.values():
                if con in draw_conect:
                    continue
                draw_conect.add(con)
                f_x, f_y, scale = self.get_cordonate(
                    con.first.x, con.first.y
                    )
                s_x, s_y, scale = self.get_cordonate(con.second.x, con.second.y)
                scale = 0
                arcade.draw.draw_line(
                    f_x, f_y, s_x, s_y, arcade.color.WHITE
                    )

        # Draw zones :)
        for zone in self.graph.zones.values():
            z_x = zone.x
            z_y = zone.y

            x, y, scale = self.get_cordonate(z_x, z_y)
            arcade.draw_circle_filled(
                x, y, radius=scale * 0.30,
                color=(255, 0, 0)
                )
            name_counter = 30

            # draw the zone name
            for name in zone.name.split("_", 1)[::-1]:
                arcade.draw_text(
                    name, x - 5, y + name_counter,
                    anchor_x="center", font_size=8,
                    bold=True, font_name="calibri"
                    )
                name_counter += 10
        # Draw Drones :) TO DO

        x,y, scale = self.get_cordonate(self.graph.start.x, self.graph.start.y)
        arcade.draw_texture_rect(self.d_image, arcade.LBWH(x - 20, y - 20, 40, 40))

