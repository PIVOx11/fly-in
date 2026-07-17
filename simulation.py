from Graph import Graph, Zone, Drone
from collections import deque
import heapq
from collections import defaultdict
from typing import Any


class Path:

    def __init__(self, cost: int, path: list[Zone]):
        self.assign: list[Drone] = []
        self.cost = cost
        self.path = path

    def __repr__(self) -> str:
        return (
                f"Path: {[zone.name for zone in self.path]}\n"
                f"Cost: {self.cost}\n"
                "asigned to: "
                f"{self.assign if self.assign else 'NO DRONE YET'}\n\n"
            )


class Simulation:
    def __init__(self, graph: Graph):
        self.graph: Graph = graph
        self.paths: list[Path] = []

    def bfs_search(
            self, start: Zone, target: Zone
            ) -> list[tuple[str, int]] | None:
        queue = deque([start])
        visited = {start}
        parent = {start: None}

        while queue:
            zone: Any = queue.popleft()

            if zone == target:
                path = []
                total = 0
                while zone is not None:
                    total += zone.get_cost()
                    path.append((zone.name, zone.get_cost()))
                    zone = parent[zone]
                return path[::-1]

            for connection in zone.connections.values():
                n = connection.first if connection.first != zone\
                    else connection.second
                if n not in visited:
                    visited.add(n)
                    parent[n] = zone
                    queue.append(n)

        return None

    def drone_path(self) -> list[Path]:
        for path in self.yen(4):
            self.paths.append(Path(path[0], path[1]))

        for drone in self.graph.drones:
            best_path = min(self.paths, key=lambda x: x.cost + len(x.assign))
            best_path.assign.append(drone)
            drone.update_data(best_path.path)

        return self.paths

    def create_drones(self) -> None:
        for id in range(1, self.graph.drone_count + 1):
            self.graph.drones.append(Drone(id))
        self.graph.start.drones = self.graph.drones[:]

    def run(self) -> dict[int, list[dict[Drone, str]]]:
        self.create_drones()
        self.drone_path()
        sim_data: dict[int, list[dict[Drone, str]]] = {}
        turns: int = 0
        moves = []

        while not self.graph.is_over():
            turns += 1
            sim_data[turns] = []

            for drone in self.graph.drones:

                if drone.finish or drone in moves:
                    continue

                if drone.can_move():
                    moves.append(drone)
                    drone.curent_zone.drones.remove(drone)
                    drone.next_zone.incoming += 1
                    drone.connect.incoming += 1
                    if drone.next_zone.zone_type == "restricted":
                        drone.to_arrive = 2

            for drone in moves[:]:

                if drone.next_zone.zone_type == "restricted":
                    destination = drone.Execute_restricted()
                else:
                    destination = drone.Execute_move()

                if drone.to_arrive == 0:
                    moves.remove(drone)
                sim_data[turns].append({drone: destination})

        return sim_data

    def djikstra(self, start: Zone, target: Zone) -> list[Zone] | None:
        """
            Find The most cheapest Path from
            stariting slected Zone to a target Zone :)
        """

        visited = set()
        parent = {start: None}
        distance: defaultdict = defaultdict(lambda: float("inf"))
        distance[start] = 0
        queue: list = []
        path = []

        heapq.heappush(queue, (0, start.name))

        while queue:
            cost, zone = heapq.heappop(queue)
            zone = self.graph.zones[zone]

            if zone in visited:
                continue

            visited.add(zone)

            if zone == target:
                total = 0

                while zone:
                    total += zone.get_cost()
                    path.append(zone)
                    zone = parent[zone]

                return path[::-1]

            for connection in zone.connections.values():
                neighbor = connection.other(zone)

                if neighbor.zone_type == "blocked" or not connection.active:
                    continue

                if neighbor.zone_type == "priority":
                    cost = 0.7
                else:
                    cost = neighbor.get_cost()
                new_dis = distance[zone] + cost

                if distance[neighbor] > new_dis:
                    distance[neighbor] = new_dis
                    parent[neighbor] = zone
                    heapq.heappush(queue, (new_dis, neighbor.name))

        return None

    def yen(self, path_count: int) -> list[tuple[int, list[Zone]]]:
        valid_paths: list[tuple[int, list[Zone]]] = []

        path = self.djikstra(self.graph.start, self.graph.end)
        valid_paths.append(self.get_path_cost(path))
        candidates = []
        c_to_remove = set()
        old_path: Any

        while len(valid_paths) < path_count:
            path = valid_paths[-1][1]
            for i in range(len(path) - 1):

                root = path[:i + 1]
                connection = root[-1].connections[path[i + 1].name]
                c_to_remove.add(connection)

                for old_path in valid_paths:
                    old_path = old_path[1]

                    if len(old_path) <= i:
                        continue

                    path_root = old_path[:i + 1]
                    if root == path_root:
                        c_to_remove.add(
                            path_root[-1].connections[old_path[i + 1].name])

                self.connections_handler(c_to_remove, True)
                cand = self.djikstra(root[-1], self.graph.end)
                self.connections_handler(c_to_remove, False)
                c_to_remove.clear()

                if not cand:
                    continue

                cand = root[:-1] + cand
                candidates.append(self.get_path_cost(cand))

            while candidates:
                best = min(candidates, key=lambda p: p[0])
                candidates.remove(best)

                if best in valid_paths:
                    continue

                valid_paths.append(best)
                break
            else:
                break

        return valid_paths

    def get_path_cost(self, path: list[Zone] | Any) -> tuple[int, list[Zone]]:
        cost = 0

        for zone in path:
            cost += zone.get_cost()

        return (cost - 1, path)

    def connections_handler(self, connections: set, active: bool) -> None:
        if active:
            for c in connections:
                c.active = False
            return

        for c in connections:
            c.active = True

    def output(self, simulation: dict) -> None:
        if not simulation:
            return
        from rich import print as r_print
        COLORS = {
            "default": "grey70", "black": "black",
            "white": "white", "grey": "grey70",
            "gray": "grey70", "red": "red",
            "darkred": "dark_red", "maroon": "dark_red",
            "crimson": "red3", "firebrick": "red3",
            "salmon": "salmon1", "pink": "hot_pink",
            "orange": "orange3", "coral": "coral",
            "gold": "yellow", "yellow": "yellow",
            "khaki": "khaki1", "green": "green",
            "lime": "green3", "olive": "olive",
            "forest": "green4", "darkgreen": "dark_green",
            "spring": "spring_green3", "blue": "blue",
            "navy": "navy_blue", "sky": "sky_blue1",
            "cyan": "cyan", "teal": "cyan3",
            "turquoise": "turquoise2", "aqua": "bright_cyan",
            "purple": "magenta", "violet": "violet",
            "indigo": "purple4", "lavender": "plum1",
            "magenta": "magenta", "brown": "brown",
            "tan": "tan", "chocolate": "sandy_brown",
            "silver": "grey85", "beige": "wheat1",
            "rainbow": "bold bright_magenta",
            }

        for turn, data in simulation.items():
            r_print(
                f"[cyan][italic][bold]Turn{turn}: "
                "[/italic][/bold][/cyan]", end=""
                )

            for move in data:
                (drone, dest), = move.items()

                if "-" in dest:
                    zone1, zone2 = dest.split('-')
                    zone1, zone2 = self.graph.zones[zone1], \
                        self.graph.zones[zone2]

                    color1, color2 = zone1.color.lower(), zone2.color.lower()

                    if color1 not in COLORS:
                        color1 = "default"

                    if color2 not in COLORS:
                        color2 = "default"

                    color1 = COLORS[color1]
                    color2 = COLORS[color2]

                    r_print(
                        f"{drone}-[{color1}]{zone1.name}-[/{color1}]",
                        end=""
                    )
                    r_print(
                        f"[{color2}]-{zone2.name}[/{color2}]", end=" "
                    )

                else:
                    zone = self.graph.zones[dest]
                    color = zone.color.lower()

                    if color not in COLORS:
                        color = "default"

                    color = COLORS[color]
                    r_print(
                        f"{drone}-[{color}]{zone.name}[/{color}]", end=" "
                        )
            print()
        r_print(
            f"\n[italic][bold][cyan]Simulation Done withen {turn}"
            " Turn .[/cyan][/italic][/bold]\n"
            )
