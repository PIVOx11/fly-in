class Drone:

    def __init__(self, id: int):
        self.id = id
        self.path = []
        self.index = 0
        self.to_arrive = 0
        self.finish = False
        self.next_zone: Zone = None
        self.prev_zone: Zone = None
        self.connect = Connection

    def update_data(self, path = None):

        if path:
            self.path = path

        self.curent_zone = self.path[self.index]

        if self.index >= len(self.path) - 1:
            return

        self.next_zone = self.path[self.index + 1]
        self.connect = self.curent_zone.connections[self.next_zone.name]

    def Execute_restricted(self):
        self.to_arrive -= 1

        if self.to_arrive == 1:
            self.connect.drones.append(self)
            self.connect.incoming -= 1
            return f"{self.curent_zone.name}-{self.next_zone.name}"
        else:
            self.connect.drones.remove(self)
            self.next_zone.incoming -= 1
            self.next_zone.drones.append(self)
            self.index += 1
            self.update_data()

            if self.index >= len(self.path) - 1:
                self.finish = True

        return self.curent_zone.name

    def Execute_move(self):
        """
            Execute The drone Move
        """

        self.next_zone.incoming -= 1
        self.connect.incoming -= 1
        self.index += 1
        self.next_zone.drones.append(self)

        self.update_data()
        if self.index >= len(self.path) - 1:
            self.finish = True

        return self.curent_zone.name

    def can_move(self) -> bool:
        """
            check if drone can move base on the Zone and connection capacity :)
        """
        if self.next_zone.can_fitt() and self.connect.can_delever():
            return True
        return False


    def __repr__(self):
        return f"D{self.id}"


class Zone:

    def __init__(
            self,
            name: str,
            x: int, y: int,
            connections: list | None = None,
            color: str | None = None,
            zone_type: str = "normal",
            max_drones: int = 1
            ):
        self.name = name
        self.x = x
        self.y = y
        self.connections = connections or {}
        self.color = color
        self.max_drones = max_drones
        self.drones: list[Drone] = []
        self.zone_type = zone_type
        self.incoming = 0 # How many dron are coming to the zone at the next turn :)

    def can_fitt(self) -> bool:
        return self.incoming + len(self.drones) < self.max_drones

    def get_cost(self):
        if self.zone_type == "priority" or self.zone_type == "normal":
            return 1
        elif self.zone_type == "restricted":
            return 2

    def get_connection(self, zone):
        return self.connections.get(zone)

    def __repr__(self):
        conect = []
        for c in self.connections.values():
            if c.first == self:
                conect.append(c.second.name)
            else:
                conect.append(c.first.name)
        return (
            f"===== Name: {self.name} ======"
            f"\nCordonates: {self.x, self.y}"
            f"\nConnectios: {conect}"
            f"\nDrones[{self.drones or 'empty'}]"
            f"\nCapacity: {self.max_drones}"
            f"\ncost: {self.get_cost()}\n"
            f"\nZone_type: {self.zone_type}\n"
        )


class Connection:
    def __init__(
            self,
            first: Zone,
            second: Zone,
            capacity: int = 1
            ):
        self.first = first
        self.second = second
        self.capacity = capacity
        self.drones = []
        self.incoming = 0
        self.active = True

    def can_delever(self):
        return len(self.drones) + self.incoming < self.capacity

    def other(self, zone):
        if zone == self.first:
            return self.second
        return self.first

    def __repr__(self):
        size = self.capacity
        return (f"{self.first.name} <---> {self.second.name} : "
                f"dron_capacity={size}")


class Graph:
    def __init__(self):
        self.drones = []
        self.zones: dict = {}
        self.start: Zone = None
        self.end: Zone = None
        self.size = 0
        self.drone_count = 0
        self.delevred = 0
        self.simulation_end = False

    def add_zone(self, zone):
        self.zones[zone.name] = zone

    def add_connection(self,
                       first: Zone,
                       second: Zone,
                       capacity: int = 1):
        connection = Connection(first, second, capacity)
        first.connections[second.name] = connection
        second.connections[first.name] = connection
    
    def is_over(self) -> bool:
        """
            Check if the simulation over by counting drones iside the end hub,
            if it equal to the drone count it mean it's over,
            all drones at the end hub
        """
        return len(self.end.drones) >= self.drone_count

    def __repr__(self):
        repr = [
            f"Start_hub:\n {self.start}",
            f"End_hub:\n {self.end}",
            "",
            "Zones:"
            ]
        for z in self.zones.values():
            repr.append(str(z))
        return "\n".join(repr)
