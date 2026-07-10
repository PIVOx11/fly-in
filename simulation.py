from error_handling import MapError
from Graph import Graph, Zone, Drone, Connection
from collections import deque
import heapq
from collections import defaultdict


class Path:

    def __init__(self, cost: int, path: list[Zone]):
        self.assign: list[Drone] = []
        self.cost = cost
        self.path = path

    def __repr__(self):
        return (
                f"Path: {[zone.name for zone in self.path]}\n"
                f"Cost: {self.cost}\n"
                f"asigned to: {self.assign if self.assign else 'NO DRONE YET'}\n\n"
            )


class Simulation:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.paths = []

    def graph_validate(self) -> list[Zone] | None:
        path = self.bfs_search(self.graph.start, self.graph.end)
        if not path:
            raise MapError(
                "There is no path between start and end point .")

    def bfs_search(self, start: Zone, target: Zone):
        queue = deque([start])
        visited = {start}
        parent = {start: None}

        while queue:
            zone = queue.popleft()

            if zone == target:
                path = []
                total = 0
                while zone is not None:
                    total += zone.get_cost()
                    path.append((zone.name, zone.get_cost()))
                    zone = parent[zone]
                return path[::-1], f"Total is {total - 1}"

            for connection in zone.connections.values():
                n = connection.first if connection.first != zone\
                    else connection.second
                if n not in visited or n.zone_type == "blocked":
                    visited.add(n)
                    parent[n] = zone
                    queue.append(n)
        return "Not Foud"

    def drone_path(self):
        for path in self.pivox_algo(self.graph.drone_count):
            self.paths.append(Path(path[0], path[1]))
        for drone in self.graph.drones:
            best_path = min(self.paths, key=lambda x: x.cost + len(x.assign))
            best_path.assign.append(drone)
            drone.path = best_path.path
        return self.paths

    def run(self):
        self.drone_path()
        con_to_free: dict[Connection, int] = defaultdict(int)
        sim_data: dict[int, list[dict[Zone, list[Drone]]]] = {} 
        # Example of sim_data = 3 : ["start": [D3, D4]]
        turns: int = 0
        moves = []

        while not self.graph.is_over():
            # check move ability
            print(f"### Turns {turns}: ###")
            for drone in self.graph.drones:

                if drone.finish:
                    continue

                drone.update_data() # Could remove :)

                if drone.can_move():
                    moves.append(drone)
                    drone.prev_zone.drones.remove(drone)
                    drone.next_zone.incoming += 1
                    drone.connect.incoming += 1
                    con_to_free[drone.connect] += 1

            # Start Execute the Moves That we decide :)

            sim_data[turns] = []

            for drone in moves:
                
                print(f"{drone} {drone.next_zone.name}")

            turns += 1






    def djikstra(self, start: Zone, target: Zone, path=[]) -> list[Zone] | None:
        """
            Find The most cheapest Path from stariting slected Zone to a target Zone :)
        """

        visited = {zone for zone in path}
        parent = {start: None}
        distance = defaultdict(lambda: float("inf"))
        distance[start] = 0
        queue = []
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
                    cost = 0.9
                else:
                    cost = neighbor.get_cost()
                new_dis = distance[zone] + cost

                if distance[neighbor] > new_dis:
                    distance[neighbor] = new_dis
                    parent[neighbor] = zone
                    heapq.heappush(queue, (new_dis, neighbor.name))

        return None

    def pivox_algo(self, path_count: int):
        valid_paths: list[tuple[int, list[Zone]]] = []

        path = self.djikstra(self.graph.start, self.graph.end)
        valid_paths.append(self.get_path_cost(path))
        candidates = []
        c_to_remove = set()

        while len(valid_paths) < path_count:
            path = valid_paths[-1] # Back to it later :)
            path = path[1] # Back to it later :)
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
                        c_to_remove.add(path_root[-1].connections[old_path[i + 1].name])

                self.connections_handler(c_to_remove, True)
                cand = self.djikstra(root[-1], self.graph.end, root[:-1])
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

    def get_path_cost(self, path: list[Zone]) -> tuple[int, list[Zone]]:
        cost = 0

        for zone in path:
            cost += zone.get_cost()

        return (cost - 1, path)

    def connections_handler(self, connections: Connection | list[Connection], active: bool) -> None:
        if active:
            for c in connections:
                c.active = False
            return

        for c in connections:
            c.active = True
