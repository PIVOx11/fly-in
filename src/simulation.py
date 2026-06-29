from .error_handling import SimulationError
from .Graph import Graph, Zone, Dron
from collections import deque


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
                    path.append(zone)
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

    def run(self):
        path = self.bfs_search(self.graph.start, self.graph.end)
        for drone in self.graph.start.drones:
            drone.path = path
        turnes = 1
        
        while not self.graph.simulation_end:
            if self.graph.delevred == self.graph.drone_count:
                self.graph.simulation_end = True
            print(f"Turnes {turnes}: ")
            for drone in self.graph.drones:
                if drone.path_pos == len(drone.path) - 1:
                    self.graph.delevred += 1
                    continue
                self.can_move(drone)

    def can_move(self, drone: Dron):
        # cheak the connection capacity
        # check the zone capacity

        if not drone.path[drone.path_pos].is_full():