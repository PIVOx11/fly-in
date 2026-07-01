class Drone:
    def __init__(self, id: int):
        self.id = id
        self.path = []
        self.index = 0
        self.finish = False

    def __repr__(self):
        return f"Drone Id: {self.id}"


class Zone:
    def __init__(
            self,
            name: str,
            x: int, y: int,
            connections: list | None = None,
            color: str | None = None,
            zone_type: str = None,
            max_drones: int = 1
            ):
        self.name = name
        self.cost = zone_type
        self.x = x
        self.y = y
        self.connections = connections or {}
        self.color = color
        self.max_dron = max_drones
        self.drones: list[Drone] = []

    def is_full(self) -> bool:
        if len(self.drones) >= self.max_dron:
            return True
        return False
    
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
            f"\nCapacity: {self.max_dron}"
            f"\ncost: {self.cost}\n"
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
        self.to_delever = 0

    def can_delever(self):
        if self.to_delever >= self.capacity:
            return False
        return True

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
