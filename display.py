import math
from collections import deque
from random import choice, random, uniform
from time import sleep
from typing import Any

import arcade

from Graph import Graph, Drone


class Display(arcade.Window):
    """
        Arcade window responsible for visualizing the drone simulation.

        This class renders the graph, animates drone movements between turns,
        displays the simulation progress, and handles user interaction.
    """

    # Accent palette pulled from the nebula background (violet / cyan / pink
    # / gold) so every drone, glow and highlight feels like it belongs to
    # the same night sky instead of clashing with it.
    ACCENTS = [
        (167, 139, 250),   # soft violet
        (56, 197, 248),    # sky cyan
        (244, 114, 182),   # nebula pink
        (250, 204, 21),    # starlight gold
        (129, 230, 217),   # aurora teal
    ]

    def __init__(
            self, sim_data: dict[int, list[dict[Drone, str]]], graph: Graph
            ):
        """
            Initialize the visualization window and prepare
            the simulation state.
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

        # --- new: animation clock driving every pulse / glow / breathing
        # effect in the scene ---
        self.time_elapsed: float = 0.0
        self.controls_alpha: float = 255.0
        self.flash_alpha: float = 0.0

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

        # a short fading trail behind every drone, and a stable accent
        # colour per drone id so you can tell them apart at a glance
        self.trails: dict[int, deque] = {
            drone.id: deque(maxlen=18) for drone in graph.drones
        }
        self.drone_accent = {
            drone.id: self.ACCENTS[i % len(self.ACCENTS)]
            for i, drone in enumerate(graph.drones)
        }

        # edges currently being traveled this turn get a bright animated
        # glow instead of the flat idle line
        self.active_edges: set[frozenset] = set()

        # a handful of lightweight shooting stars drifting through the sky
        # region of the background, purely decorative
        self.shooting_stars: list[dict] = []
        self.shooting_star_timer = uniform(2.0, 5.0)

        self.play = True
        self.show_trails = True
        self.show_glow = True

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

    # ------------------------------------------------------------------
    # update / simulation stepping
    # ------------------------------------------------------------------

    def on_update(self, delta_time: float) -> None:
        """
            Update the animation every frame.
        """

        self.time_elapsed += delta_time

        if self.controls_alpha > 0:
            self.controls_alpha = max(
                0.0, self.controls_alpha - delta_time * 60
                )

        if self.flash_alpha > 0:
            self.flash_alpha = max(0.0, self.flash_alpha - delta_time * 220)

        self._update_shooting_stars(delta_time)

        if not self.play:
            return

        if self.curent_turn > len(self.sim_data):
            return

        if self.dron_progress >= 1:
            sleep(0.09)
            self.curent_turn += 1
            self.flash_alpha = 35.0
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

        if self.show_trails:
            for drone_id, visual in self.dis_drones.items():
                if visual["moving"]:
                    self.trails[drone_id].append(
                        (visual["x"], visual["y"])
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
        self.active_edges = set()

        for move in self.sim_data.get(self.curent_turn, []):
            if not move:
                break

            for drone, dest in move.items():
                start_x = self.dis_drones[drone.id]["target_x"]
                start_y = self.dis_drones[drone.id]["target_y"]

                if "-" in dest:
                    start, dest = dest.split("-")
                    self.active_edges.add(frozenset((start, dest)))
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

    def _update_shooting_stars(self, delta_time: float) -> None:
        """
            Spawn and animate small shooting stars drifting across the
            upper part of the sky, purely for atmosphere.
        """
        self.shooting_star_timer -= delta_time
        if self.shooting_star_timer <= 0:
            self.shooting_star_timer = uniform(3.5, 7.5)
            start_x = uniform(self.width * 0.1, self.width * 0.9)
            start_y = uniform(self.height * 0.65, self.height * 0.95)
            angle = uniform(200, 250)
            speed = uniform(260, 420)
            self.shooting_stars.append({
                "x": start_x,
                "y": start_y,
                "vx": math.cos(math.radians(angle)) * speed,
                "vy": math.sin(math.radians(angle)) * speed,
                "life": 1.0,
            })

        for star in self.shooting_stars:
            star["x"] += star["vx"] * delta_time
            star["y"] += star["vy"] * delta_time
            star["life"] -= delta_time * 0.9

        self.shooting_stars = [
            s for s in self.shooting_stars if s["life"] > 0
            ]

    # ------------------------------------------------------------------
    # drawing
    # ------------------------------------------------------------------

    def draw_score(self) -> None:
        """
            Draw the current simulation turn counter and a small status
            panel (speed, drone count, play/pause state).
        """

        turn = min(self.curent_turn, len(self.sim_data))
        total = len(self.sim_data)
        score = f"TURN  {turn} / {total}"

        panel_w, panel_h = 230, 64
        panel_x, panel_y = 16, self.height - panel_h - 16

        arcade.draw_rect_filled(
            arcade.LBWH(panel_x, panel_y, panel_w, panel_h),
            (18, 12, 40, 150)
            )
        arcade.draw_rect_outline(
            arcade.LBWH(panel_x, panel_y, panel_w, panel_h),
            (167, 139, 250, 160), border_width=1.5
            )

        arcade.draw_text(
            score, panel_x + 16, panel_y + panel_h - 30,
            arcade.color.WHITE, 16,
            bold=True, font_name="calibri"
        )

        speed_pct = round(self.drone_speed * 100)
        arcade.draw_text(
            f"SPEED  {speed_pct}%   |   DRONES  {len(self.dis_drones)}",
            panel_x + 16, panel_y + 12,
            (200, 190, 255), 11, font_name="calibri"
        )

        self._draw_play_state_icon(panel_x + panel_w - 26, panel_y + 16)

    def _draw_play_state_icon(self, x: float, y: float) -> None:
        """Small play / pause glyph in the status panel."""
        if self.play:
            arcade.draw_triangle_filled(
                x - 5, y - 7, x - 5, y + 7, x + 7, y,
                (129, 230, 217, 220)
            )
        else:
            arcade.draw_rect_filled(
                arcade.LBWH(x - 6, y - 7, 4, 14), (244, 114, 182, 220)
                )
            arcade.draw_rect_filled(
                arcade.LBWH(x + 2, y - 7, 4, 14), (244, 114, 182, 220)
                )

    def draw_controls_hint(self) -> None:
        """Fading reminder of the keyboard shortcuts, shown briefly."""
        if self.controls_alpha <= 0:
            return

        a = self.controls_alpha
        text = "SPACE pause   \u2191/\u2193 speed   R restart   ESC quit"
        arcade.draw_text(
            text, self.width - 16, 16,
            (255, 255, 255, int(a)), 12,
            anchor_x="right", font_name="calibri", bold=True
        )

    def on_draw(self) -> None:
        """
            Render the current simulation frame.
        """
        self.clear()

        self._draw_background()
        self._draw_shooting_stars()

        draw_conect = set()

        # draw connections (idle dim, active edges glowing)
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

                edge_key = frozenset((con.first.name, con.second.name))
                if edge_key in self.active_edges:
                    self._draw_glow_line(
                        f_x, f_y, s_x, s_y, (250, 204, 21)
                        )
                else:
                    arcade.draw_line(
                        f_x, f_y, s_x, s_y, (200, 190, 235, 70), line_width=1.5
                        )

        # Draw zones :)
        default_color = arcade.color.GRAY

        for i, zone in enumerate(self.graph.zones.values()):
            zone_color = getattr(
                arcade.color, zone.color, default_color)
            if zone.color == "RAINBOW":
                zone_color = getattr(
                    arcade.color, choice(self.colors), default_color)

            z_x = zone.x
            z_y = zone.y

            x, y, scale = self.get_cordonate(z_x, z_y)

            pulse = 1 + 0.08 * math.sin(self.time_elapsed * 1.6 + i * 0.7)
            radius = scale * 0.30 * pulse

            if self.show_glow:
                self._draw_soft_glow(x, y, radius, zone_color)

            arcade.draw_circle_filled(
                x, y, radius=radius,
                color=zone_color
                )
            arcade.draw_circle_outline(
                x, y, radius + 1.5,
                (255, 255, 255, 55), border_width=1.5
                )

            name_counter = scale / 3

            # draw the zone name
            for name in zone.name.split("_", 1)[::-1]:
                arcade.draw_text(
                    name, x - 5, y + name_counter + 3,
                    (12, 8, 24, 200), font_size=8,
                    anchor_x="center", bold=True, font_name="calibri"
                    )
                arcade.draw_text(
                    name, x - 5, y + name_counter,
                    anchor_x="center", font_size=8,
                    bold=True, font_name="calibri"
                    )
                name_counter += 10

        # drone trails, drawn before the drones so drones sit on top
        if self.show_trails:
            for drone_id, trail in self.trails.items():
                accent = self.drone_accent[drone_id]
                n = len(trail)
                for idx, (tx, ty) in enumerate(trail):
                    cx, cy, scale = self.get_cordonate(tx, ty)
                    fade = (idx + 1) / max(n, 1)
                    alpha = int(70 * fade)
                    r = scale * 0.05 * (0.4 + fade)
                    arcade.draw_circle_filled(
                        cx, cy, max(r, 1.0), (*accent, alpha)
                        )

        for id in self.dis_drones:
            drone = self.dis_drones[id]
            self.draw_drone(id, drone["x"], drone["y"])

        # subtle full-turn flash so a new turn "reads" without being loud
        if self.flash_alpha > 0:
            arcade.draw_rect_filled(
                arcade.LBWH(0, 0, self.width, self.height),
                (255, 255, 255, int(self.flash_alpha * 0.15))
                )

        self.draw_score()
        self.draw_controls_hint()

    def _draw_background(self) -> None:
        """Draw the night-sky background with a slow, gentle breathing
        zoom so the scene never feels static."""
        if not self.background_image:
            return

        zoom = 1 + 0.015 * math.sin(self.time_elapsed * 0.3)
        w = self.width * zoom
        h = self.height * zoom
        x = (self.width - w) / 2
        y = (self.height - h) / 2

        arcade.draw_texture_rect(
            self.background_image,
            arcade.LBWH(x, y, w, h))

    def _draw_shooting_stars(self) -> None:
        for star in self.shooting_stars:
            alpha = int(255 * max(0.0, star["life"]))
            tail_x = star["x"] - star["vx"] * 0.05
            tail_y = star["y"] - star["vy"] * 0.05
            arcade.draw_line(
                tail_x, tail_y, star["x"], star["y"],
                (255, 255, 255, alpha), line_width=2
                )

    def _draw_soft_glow(
            self, x: float, y: float, radius: float, color
            ) -> None:
        """Cheap radial glow made of a few translucent rings."""
        r, g, b = color[0], color[1], color[2]
        for i, mult in enumerate((2.0, 1.6, 1.2)):
            alpha = int(14 / (i + 1))
            arcade.draw_circle_filled(
                x, y, radius * mult, (r, g, b, alpha)
                )

    def _draw_glow_line(
            self, x1: float, y1: float, x2: float, y2: float, color
            ) -> None:
        """Bright animated line for edges a drone is actively crossing."""
        r, g, b = color
        pulse = 0.5 + 0.5 * math.sin(self.time_elapsed * 4)
        arcade.draw_line(x1, y1, x2, y2, (r, g, b, 22), line_width=6)
        arcade.draw_line(x1, y1, x2, y2, (r, g, b, 50), line_width=3)
        arcade.draw_line(
            x1, y1, x2, y2,
            (255, 255, 255, int(80 + 45 * pulse)), line_width=1.5
            )

    def draw_drone(self, id: int, x: int, y: int) -> None:
        """
            Draw a single drone at the given graph coordinates.
        """
        cx, cy, scale = self.get_cordonate(x, y)
        accent = self.drone_accent.get(id, (250, 204, 21))

        if self.show_glow:
            self._draw_soft_glow(cx, cy, scale * 0.22, accent)

        arcade.draw_circle_filled(
            cx, cy, scale * 0.2, arcade.color.YELLOW
            )

        arcade.draw_circle_outline(
            cx, cy, scale * 0.2 + 2, (*accent, 180),
            border_width=3
            )
        arcade.draw_circle_outline(
            cx, cy, scale * 0.2 + 2, arcade.color.BLACK,
            border_width=1
            )

        arcade.draw_text(
            str(id), cx, cy, arcade.color.BLACK, scale * 0.15,
            anchor_x="center", anchor_y="center", bold=True,
            )

    def get_cordonate(
            self, x: int, y: int) -> tuple[int, int, int]:
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
                T      Toggle drone trails.
                G      Toggle glow effects.
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
            for trail in self.trails.values():
                trail.clear()
            self.active_edges = set()

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

        if key == arcade.key.T:
            self.show_trails = not self.show_trails
            if not self.show_trails:
                for trail in self.trails.values():
                    trail.clear()

        if key == arcade.key.G:
            self.show_glow = not self.show_glow

        if key == arcade.key.ESCAPE:
            arcade.exit()
