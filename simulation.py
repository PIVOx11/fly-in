from error_handling import SimulationError
from Graph import Graph, Zone, Drone, Connection
from collections import deque
import heapq
from collections import defaultdict

class Simulation:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.path = []

    def graph_validate(self) -> list[Zone] | None:
        path = self.bfs_search(self.graph.start, self.graph.end)
        if not path:
            raise SimulationError(
                "There is no path between start and end point .")
        print(path)

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

    def pivox_algo(self, path_count: int) -> list:
        valid_paths: list[tuple[int, list[Zone]]] = []

        path = self.djikstra(self.graph.start, self.graph.end)
        valid_paths.append(path)
        candidates = []
        
        while len(valid_paths) < path_count:
            path = valid_paths[-1]

            for i in range(len(path) - 1):
                root = path[:i + 1]
                connection = root[-1].connections[path[i + 1].name]
                connection.active = False
                cand = self.djikstra(root[-1], self.graph.end, root[:-1])
                connection.active = True

                if not cand:
                    continue

                cand = root[:-1] + cand
                candidates.append(self.get_path_cost(cand))
            
            while candidates:
                best = min(candidates, key=lambda p: p[0])
                candidates.remove(best)

                if best[1] in valid_paths:
                    continue

                valid_paths.append(best[1])
                break
            else:
                break

        return valid_paths

    def get_path_cost(self, candidate):
        cost = 0

        for zone in candidate:
            cost += zone.get_cost()

        return (cost, candidate)
