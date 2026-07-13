import arcade
import math

class DroneVisualizerApp(arcade.Window):
    def __init__(self, graph, sim_data):
        super().__init__(800, 600, "Drone Simulation Visualizer", resizable=True)
        
        self.graph = graph
        self.sim_data = sim_data
        self.current_turn = 0
        self.turn_timer = 0.0
        self.turn_duration = 0.8
        self.time_counter = 0.0
        
        # Trail storage for drones
        self.trails = {drone.id: [] for drone in self.graph.drones}
        
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)

        zones = list(self.graph.zones.values())
        self.min_x = min(z.x for z in zones) if zones else 0
        self.max_x = max(z.x for z in zones) if zones else 1
        self.min_y = min(z.y for z in zones) if zones else 0
        self.max_y = max(z.y for z in zones) if zones else 1
        
        self.vis_drones = {d.id: {"x": self.graph.start.x, "y": self.graph.start.y, 
                                  "target_x": self.graph.start.x, "target_y": self.graph.start.y,
                                  "color": arcade.color.YELLOW} for d in self.graph.drones}

    def get_screen_coords(self, logic_x, logic_y):
        padding = 80
        w, h = self.width - padding * 2, self.height - padding * 2
        dx = max(self.max_x - self.min_x, 1)
        dy = max(self.max_y - self.min_y, 1)
        scale = min(w / dx, h / dy)
        cx = (self.width - dx * scale) / 2
        cy = (self.height - dy * scale) / 2
        return cx + (logic_x - self.min_x) * scale, cy + (logic_y - self.min_y) * scale

    def on_key_press(self, key, modifiers):
        """Keyboard controls: speed up/slow down simulation."""
        if key in [arcade.key.PLUS, arcade.key.UP]:
            self.turn_duration = max(0.1, self.turn_duration - 0.1)
        elif key in [arcade.key.MINUS, arcade.key.DOWN]:
            self.turn_duration += 0.1

    def on_update(self, delta_time):
        self.time_counter += delta_time
        lerp_factor = 1.0 - math.exp(-7.0 * delta_time)
        
        # Update drone positions and record trails
        for d_id, vd in self.vis_drones.items():
            vd["x"] += (vd["target_x"] - vd["x"]) * lerp_factor
            vd["y"] += (vd["target_y"] - vd["y"]) * lerp_factor
            
            # Trail logic: record current screen position
            screen_x, screen_y = self.get_screen_coords(vd["x"], vd["y"])
            self.trails[d_id].append((screen_x, screen_y))
            if len(self.trails[d_id]) > 20: self.trails[d_id].pop(0)

        if self.current_turn + 1 > len(self.sim_data): return 
            
        self.turn_timer += delta_time
        if self.turn_timer >= self.turn_duration:
            self.turn_timer = 0.0
            for move_dict in self.sim_data.get(self.current_turn + 1, []):
                for drone, dest in move_dict.items():
                    if "-" in dest and dest not in self.graph.zones:
                        z_names = dest.split("-")
                        z1, z2 = self.graph.zones[z_names[0]], self.graph.zones[z_names[1]]
                        self.vis_drones[drone.id].update({"target_x": (z1.x + z2.x)/2, "target_y": (z1.y + z2.y)/2})
                    else:
                        zone = self.graph.zones[dest]
                        self.vis_drones[drone.id].update({"target_x": zone.x, "target_y": zone.y})
            self.current_turn += 1

    def on_draw(self):
            self.clear()
            
            # Draw UI
            arcade.draw_text(f"Turn: {self.current_turn} | Speed (Delay): {self.turn_duration:.1f}s", 
                            20, self.height - 30, arcade.color.WHITE, 14, bold=True)

            # 1. Draw Connections in Grey
            drawn_conns = set()
            for zone in self.graph.zones.values():
                for conn in zone.connections.values():
                    if conn not in drawn_conns:
                        x1, y1 = self.get_screen_coords(conn.first.x, conn.first.y)
                        x2, y2 = self.get_screen_coords(conn.second.x, conn.second.y)
                        # Connections drawn in grey
                        arcade.draw_line(x1, y1, x2, y2, arcade.color.GRAY, 2)
                        drawn_conns.add(conn)

            # 2. Draw Trails
            for d_id, trail in self.trails.items():
                for i in range(len(trail) - 1):
                    arcade.draw_line(trail[i][0], trail[i][1], trail[i+1][0], trail[i+1][1], 
                                    (255, 255, 0, 100), 2)

            # 3. Draw Zones with Glow
            for zone in self.graph.zones.values():
                x, y = self.get_screen_coords(zone.x, zone.y)
                color = getattr(arcade.color, zone.color.upper(), arcade.color.PASTEL_GREEN) if zone.color and zone.color != "LATER" else arcade.color.PASTEL_GREEN
                
                for i in range(5):
                    arcade.draw_circle_filled(x, y, 15 + i*2, (*color[:3], 40 - i*8))
                
                arcade.draw_circle_filled(x, y, 15, color)
                arcade.draw_text(zone.name, x, y + 18, arcade.color.WHITE, 8, anchor_x="center")

            # 4. Draw Drones with pulse
            pulse = (math.sin(self.time_counter * 8) * 3) + 9 
            for d_id, vd in self.vis_drones.items():
                x, y = self.get_screen_coords(vd["x"], vd["y"])
                arcade.draw_circle_filled(x, y, pulse, vd["color"])
                arcade.draw_text(f"D{d_id}", x, y - 4, arcade.color.BLACK, 8, anchor_x="center", bold=True)