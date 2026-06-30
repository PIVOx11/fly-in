from .error_handling import SimulationError
from .Graph import Graph, Zone, Drone
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

            for connection in zone.connections.values():
                n = connection.first if connection.first != zone\
                    else connection.second
                if n not in visited and n.zone_type != "blocked":
                    visited.add(n)
                    parent[n] = zone
                    queue.append(n)
        return None

    def run(self):
        s_path = self.bfs_search(self.graph.start, self.graph.end)
        for drone in self.graph.drones:
            drone.path = s_path

        turns = 1
        while self.graph.delevred < self.graph.drone_count:
            print(f"Turn {turns}: ==================================")
            move = []
            connections = []

            for drone in self.graph.drones:
                if drone.finish:
                    continue

                if drone.index == len(drone.path)-1:
                    drone.finish = True
                    self.graph.delevred += 1
                    continue

                next_zone = drone.path[drone.index + 1]
                connection = drone.path[drone.index].connections[next_zone.name]

                if self.can_move(drone, next_zone, connection):
                    connections.append(connection)
                    move.append(drone)

            for drone in move:
                drone.path[drone.index].drones.remove(drone)
                drone.index += 1
                print(drone, f", Move to {drone.path[drone.index].name}, max to fitt {drone.path[drone.index].max_drones}\n")
            for c in connections:
                c.to_delever -= 1
            turns += 1

    def can_move(self, drone, next_zone, connection) -> bool:
        # cheak the connection capacity
        # check the zone capacity
        
        if not drone.path[drone.index + 1].is_full():
            if connection.can_delever():
                next_zone.drones.append(drone)
                connection.to_delever += 1
                return True
        return False

