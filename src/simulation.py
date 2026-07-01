from .error_handling import SimulationError
from .Graph import Graph, Zone, Drone
from collections import deque
import heapq
from collections import defaultdict

class Simulation:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.path = []

    def run(self):
        self.graph_validate()

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
                while zone is not None:
                    path.append((zone.name, zone.cost))
                    zone = parent[zone]
                return path[::-1]

            for connection in zone.connections.values():
                n = connection.first if connection.first != zone\
                    else connection.second
                if n not in visited and n.cost <= 2:
                    visited.add(n)
                    parent[n] = zone
                    queue.append(n)
        return None

    def djikstra(self, start: Zone, target: Zone) -> list[Zone] | None:
        # Find The most cheapest Path from stariting slected Zone to a target Zone :).
        visited = set()
        parent = {start: None}
        distance = defaultdict(lambda: float("inf"))
        distance[start] = 0
        queue = []
        path = []
        c = 0
        heapq.heappush(queue, (start.cost, start.name))
        while queue:
            cost, zone = heapq.heappop(queue)

            zone = self.graph.zones[zone]
            visited.add(zone)

            if zone == target:
                while zone:
                    c += zone.cost
                    path.append((zone.name, zone.cost, c))
                    zone = parent[zone]
                return path[::-1]
            for neighbord in zone.connections.values():
                neighbord = neighbord.first if neighbord.first != zone\
                            else neighbord.second

                if neighbord.cost == float("inf") or neighbord in visited:
                    continue

                new_dis = -9 + neighbord.cost

                if new_dis < distance[neighbord]:
                    distance[neighbord] = new_dis
                    parent[neighbord] = zone
                    heapq.heappush(queue, (new_dis, neighbord.name))

        return "Not Founnnd"