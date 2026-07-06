from error_handling import SimulationError
from Graph import Graph, Zone, Drone, Connection
from collections import deque
import heapq
from collections import defaultdict

class Simulation:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.path = []

    def run(self):
        """
            Simulate the Drones movments in one path :) .
        """
        path = self.djikstra(self.graph.start, self.graph.end)
        for drone in self.graph.drones:
            drone.path = path
        turns = 1
        waiting = []
        while turns < 5:
            # print("Turn: ", turns)
            moves = []
            for drone in self.graph.drones:
                if drone.finish:
                    continue

                if drone.state == "crosing":
                    moves.append(drone)
                destination = drone.path[drone.index + 1]          # The next zone 
                connection = destination.connections[drone.path[drone.index].name]   # The connection to the next zone
                turns = 0                   # How many turn i need to cross it :)
                
                if self.can_move(destination, connection):
                    moves.append((drone, destination, connection))
                    destination.incoming += 1
                    connection.incoming += 1
                    drone.remaining = 1 if destination.zone_type == "restricted" else 0
            
            for drone, dest, connection in moves:
                if drone.remaining:
                    destination.incoming -= 1
                    connection.drones.append(drone)
                    connection.incoming -= 1
                    drone.path[drone.index].remove(drone)
                    drone.ramining -= 1
                    drone.state = "crosing"
                else:
                    destination.incoming -= 1
                    drone.move(connection)
                    print(drone, "Move to ", dest.name)
            turns += 1


    
    def can_move(self, destination: Zone,
                 connection: Connection)-> bool:
        if connection.can_delever() and destination.can_fitt():
                return True
        return False


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

    def djikstra(self, start: Zone, target: Zone) -> list[Zone] | None:
        """
            Find The most cheapest Path from stariting slected Zone to a target Zone :)
        """
        visited = set()
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
                    path.append(zone)
                    zone = parent[zone]
                return path[::-1]

            for neighbor in zone.connections.values():
                neighbor = neighbor.other(zone)

                if neighbor.zone_type == "blocked":
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
