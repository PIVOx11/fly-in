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
        self.curent_turn = 0
        self.dron_progress = 0
        self.drone_speed = 0.02
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
            return

        if self.dron_progress >= 1:
            self.curent_turn += 1
            for visual in self.dis_drones.values():
                if visual["moving"]:
                    visual["x"] = visual["target_x"]
                    visual["y"] = visual["target_y"]
            self.load_new_derections()

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

        self.dron_progress += self.drone_speed

    def load_new_derections(self):
        for drone in self.dis_drones:
            self.dis_drones[drone]["moving"] = False

        self.dron_progress = 0

        for move in self.sim_data.get(self.curent_turn, []):
            if not move:
                break

            for drone, dest in move.items():
                start_x = self.dis_drones[drone.id]["target_x"]
                start_y = self.dis_drones[drone.id]["target_y"]

                if "-" in dest:
                    start, dest = dest.split("-")
                    start = self.graph.zones[start]
                    dest = self.graph.zones[dest]
                    self.dis_drones[drone.id]["start_x"] = start_x
                    self.dis_drones[drone.id]["start_y"] = start_y
                    self.dis_drones[drone.id]["target_x"] = (start.x + dest.x) / 2
                    self.dis_drones[drone.id]["target_y"] = (start.y + dest.y) / 2
                    self.dis_drones[drone.id]["moving"] = True

                else:
                    dest = self.graph.zones[dest]
                    self.dis_drones[drone.id]["start_x"] = start_x
                    self.dis_drones[drone.id]["start_y"] = start_y
                    self.dis_drones[drone.id]["target_x"] = dest.x
                    self.dis_drones[drone.id]["target_y"] = dest.y
                    self.dis_drones[drone.id]["moving"] = True
                
    def draw_score(self):
        score = f"TURNS: {min(self.curent_turn, len(self.sim_data))} "\
                f"/ {len(self.sim_data)}"
        arcade.draw_text(
            score,100,
            self.height - 50,
            arcade.color.WHITE, 18, anchor_x="center",
            bold=True
        )
    def on_draw(self):
        self.clear()
        draw_conect = set()

        self.draw_score()
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
            name_counter = scale / 3

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

            arcade.draw_circle_filled(
                cx , cy, scale * 0.2, arcade.color.YELLOW
                )

            arcade.draw_circle_filled(
                cx, cy, scale * 0.15, (255, 255, 0, 40)
                )

            arcade.draw_text(
                str(id), cx, cy, arcade.color.BLACK, scale * 0.15,
                anchor_x="center", anchor_y="center", bold=True,
                )
            return

    def get_cordonate(self, x: int, y: int):
        MAX_SCALE = 160
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
        screen_y = start_y + y * scale

        return screen_x, screen_y, scale



    def on_key_press(self, key, modifiers):

        if key == arcade.key.R:
            self.curent_turn = 0
            self.dis_drones = {
            drone.id : {
                "x": self.graph.start.x,
                "y": self.graph.start.y,
                "start_x": self.graph.start.x,
                "start_y": self.graph.start.y,
                "target_x": self.graph.start.x,
                "target_y": self.graph.start.y,
                "moving": False
            } for drone in self.graph.drones
        }
            
        if key == arcade.key.UP:
            self.drone_speed = min(1, self.drone_speed + 0.01)

        if key == arcade.key.DOWN:
            self.drone_speed = max(0.01, self.drone_speed - 0.01)
