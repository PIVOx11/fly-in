import arcade
from Graph import Graph, Drone
from time import sleep
from random import choice
from typing import Any


class Display(arcade.Window):
    """
        Arcade window responsible for visualizing the drone simulation.

        This class renders the graph, animates drone movements between turns,
        displays the simulation progress, and handles user interaction.
    """
    def __init__(
            self, sim_data: dict[int, list[dict[Drone, str]]], graph: Graph
            ):
        """
            Initialize the visualization window and prepare the simulation state.
        """

        super().__init__(resizable=True, title="Fly-in | by: blidriss")

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
        self.dron_progress: int | float = 0
        self.drone_speed: int | float = 0.02

        self.dis_drones = {
            drone.id: {
                "x": graph.start.x,
                "y": graph.start.y,
                "start_x": graph.start.x,
                "start_y": graph.start.y,
                "target_x": graph.start.x,
                "target_y": graph.start.y,
                "moving": False
            } for drone in graph.drones
        }

        self.play = True

        self.colors = [
            "RED", "ORANGE", "YELLOW", "GREEN", "BLUE", "INDIGO",
            "VIOLET"
            ]
        try:
            self.background_image = arcade.load_texture(
                "assets/background.png")
        except Exception:
            self.background_image = None
            self.background_color = arcade.color.PURPLE

    def on_update(self, delta_time: float) -> None:
        """
            Update the animation every frame.
        """

        if not self.play:
            return

        if self.curent_turn > len(self.sim_data):
            return

        if self.dron_progress >= 1:
            sleep(0.09)
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
                    self.dis_drones[drone]["target_x"] -
                    self.dis_drones[drone]["start_x"]
                ) * self.dron_progress
            )

            self.dis_drones[drone]["y"] = (
                            self.dis_drones[drone]["start_y"] + (
                                self.dis_drones[drone]["target_y"] -
                                self.dis_drones[drone]["start_y"]
                            ) * self.dron_progress
            )

        self.dron_progress += self.drone_speed

    def load_new_derections(self) -> None:
        """
            Load the movements scheduled for the current simulation turn.
        """
        drone: Drone | int

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
                    self.dis_drones[drone.id]["target_x"] =\
                        (start.x + dest.x) / 2
                    self.dis_drones[drone.id]["target_y"] =\
                        (start.y + dest.y) / 2
                    self.dis_drones[drone.id]["moving"] = True

                else:
                    dest = self.graph.zones[dest]
                    self.dis_drones[drone.id]["start_x"] = start_x
                    self.dis_drones[drone.id]["start_y"] = start_y
                    self.dis_drones[drone.id]["target_x"] = dest.x
                    self.dis_drones[drone.id]["target_y"] = dest.y
                    self.dis_drones[drone.id]["moving"] = True

    def draw_score(self) -> None:
        """
            Draw the current simulation turn counter.
        """

        score = f"TURNS: {min(self.curent_turn, len(self.sim_data))} "\
                f"/ {len(self.sim_data)}"

        arcade.draw_text(
            score, 100,
            self.height - 50,
            arcade.color.WHITE, 18, anchor_x="center",
            bold=True, italic=True
        )

    def on_draw(self) -> None:
        """
            Render the current simulation frame.
        """
        self.clear()
        if self.background_image:
            arcade.draw_texture_rect(
                self.background_image,
                arcade.LBWH(0, 0, self.width, self.height))

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
                s_x, s_y, scale = self.get_cordonate(
                    con.second.x, con.second.y)
                scale = 0
                arcade.draw.draw_line(
                    f_x, f_y, s_x, s_y, arcade.color.WHITE
                    )

        # Draw zones :)
        default_color = arcade.color.GRAY

        for zone in self.graph.zones.values():
            zone_color = getattr(
                arcade.color, zone.color, default_color)
            if zone.color == "RAINBOW":
                zone_color = getattr(
                    arcade.color, choice(self.colors), default_color)

            z_x = zone.x
            z_y = zone.y

            x, y, scale = self.get_cordonate(z_x, z_y)

            arcade.draw_circle_filled(
                x, y, radius=scale * 0.30,
                color=zone_color
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

    def draw_drone(self, id: int, x: int, y: int) -> None:
        """
            Draw a single drone at the given graph coordinates.
        """
        cx, cy, scale = self.get_cordonate(x, y)

        arcade.draw_circle_filled(
            cx, cy, scale * 0.2, arcade.color.YELLOW
            )

        arcade.draw_circle_outline(
            cx, cy, scale * 0.2 + 2, arcade.color.BLACK,
            border_width=3
            )

        arcade.draw_text(
            str(id), cx, cy, arcade.color.BLACK, scale * 0.15,
            anchor_x="center", anchor_y="center", bold=True,
            )

    def get_cordonate(
            self, x: int, y: int
        ) -> tuple[int, int, int]:
        """
            Convert graph coordinates into screen coordinates.
        """

        MAX_SCALE = 100

        graph_width = max(self.max_x - self.min_x, 1)
        graph_height = max(self.max_y - self.min_y, 1)

        available_width = self.width - self.margin
        available_height = self.height - self.margin

        scale = min(
            available_width / graph_width,
            available_height / graph_height,
            MAX_SCALE
        )

        offset_x = (self.width - graph_width * scale) / 2
        offset_y = (self.height - graph_height * scale) / 2

        screen_x = offset_x + (x - self.min_x) * scale
        screen_y = offset_y + (y - self.min_y) * scale

        return screen_x, screen_y, scale

    def on_key_press(self, key: Any, modifiers: Any) -> None:
        """
            Handle keyboard shortcuts controlling the visualization.

            Controls:
                R      Restart the simulation.
                UP     Increase animation speed.
                DOWN   Decrease animation speed.
                SPACE  Pause or resume the animation.
                ESC    Close the application.
        """
        if key == arcade.key.R:
            self.curent_turn = 0
            self.dis_drones = {
                drone.id: {
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
            self.drone_speed = min(
                1, self.drone_speed + 0.01
                )

        if key == arcade.key.DOWN:
            self.drone_speed = max(
                0.01, self.drone_speed - 0.01
                )

        if key == arcade.key.SPACE:
            self.play = not self.play

        if key == arcade.key.ESCAPE:
            arcade.exit()
