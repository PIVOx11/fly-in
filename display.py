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
        self.curent_turn = 1
        self.dron_progress = 1
        self.drone_speed = 0.2

        self.dis_drones = {
            drone.id : {
                "x": graph.start.x,
                "y": graph.start.y,
                "start_x": graph.start.x,
                "start_y": graph.start.y,
                "target_x": graph.start.x,
                "target_y": graph.start.y,
                "moving": False
            } for drone in graph.drones
        }

    def on_update(self, delta_time):
        if self.curent_turn > len(self.sim_data):
            for drone in self.dis_drones:
                self.dis_drones[drone]["x"] = self.dis_drones[drone]["target_x"]
                self.dis_drones[drone]["y"] = self.dis_drones[drone]["target_y"]
            return

        if self.dron_progress >= 1:
            for drone in self.dis_drones:
                self.dis_drones[drone]["moving"] = False

            self.dron_progress = 0

            for move in self.sim_data[self.curent_turn]:
                for drone, dest in move.items():
                    dest = self.graph.zones[dest]
                    self.dis_drones[drone.id]["start_x"] = self.dis_drones[drone.id]["target_x"]
                    self.dis_drones[drone.id]["start_y"] = self.dis_drones[drone.id]["target_y"]
                    self.dis_drones[drone.id]["target_x"] = dest.x
                    self.dis_drones[drone.id]["target_y"] = dest.y
                    self.dis_drones[drone.id]["moving"] = True
            self.curent_turn += 1

        for drone in self.dis_drones:
            if not self.dis_drones[drone]["moving"]:
                continue
            self.dis_drones[drone]["x"] = (
                self.dis_drones[drone]["start_x"] + (
                    self.dis_drones[drone]["target_x"] - self.dis_drones[drone]["start_x"]
                ) * self.dron_progress
            )
    
            self.dis_drones[drone]["y"] = (
                            self.dis_drones[drone]["start_y"] + (
                                self.dis_drones[drone]["target_y"] - self.dis_drones[drone]["start_y"]
                            ) * self.dron_progress
            )

        self.dron_progress += 0.09

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
        for id in self.dis_drones:
            drone = self.dis_drones[id]
            self.draw_drone(id, drone["x"], drone["y"])

    def draw_drone(self, id, x, y):
            cx, cy, scale = self.get_cordonate(x, y)
            arcade.draw_circle_filled(cx , cy, scale * 0.1, arcade.color.YELLOW)
            arcade.draw_text(id, (cx) - 8, cy - 4, arcade.color.BLACK, scale * 0.08, bold=True)
            return

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
