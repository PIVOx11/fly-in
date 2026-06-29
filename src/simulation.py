from .error_handling import SimulationError
from .Graph import Graph, Zone
from collections import deque


class Simulation:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.path = []

    def run(self):
        self.graph_validate()

    def graph_validate(self) -> list[Zone] | None:
        path = self.bfs_search(self.graph, self.graph.start, self.graph.end)
        if not path:
            raise SimulationError(
                "There is no path between start and end point .")
        print(path)

    from collections import deque

    def bfs_search(self, start: Zone, target: Zone):
        queue = deque([start])
        visited = {start}
        parent = {start: None}

        while queue:
            zone = queue.popleft()

            if zone == target:
                path = []
                while zone is not None:
                    path.append(zone.name)
                    zone = parent[zone]
                return path[::-1]

            for connection in zone.connections:
                n = connection.first if connection.first != zone\
                    else connection.second
                if n not in visited and n.zone_type != "blocked":
                    visited.add(n)
                    parent[n] = zone
                    queue.append(n)
        return None
