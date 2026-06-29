class Drone:
    def __init__(self, id: int):
        self.id = id

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
        self.zone_type = zone_type
        self.x = x
        self.y = y
        self.connections = connections or []
        self.color = color
        self.max_dron = max_drones
        self.drones: list[Drone] = []

    def __repr__(self):
        conect = []
        for c in self.connections:
            if c.first == self:
                conect.append(c.second.name)
            else:
                conect.append(c.first.name)
        return (
            f"===== Name: {self.name} ======"
            f"\nCordonates: {self.x, self.y}"
            f"\nType: {self.zone_type}"
            f"\nConnectios: {conect}"
            f"\nDrones[{self.drones or 'empty'}]\n"
        )


class Connection:
    def __init__(
            self,
            first: Zone,
            second: Zone,
            dron_capacity: int = 1
            ):
        self.first = first
        self.second = second
        self.dron_capacity = dron_capacity

    def __repr__(self):
        size = self.dron_capacity
        return (f"{self.first.name} <---> {self.second.name} : "
                f"dron_capacity={size}")


class Graph:
    def __init__(self):
        self.zones: dict = {}
        self.start: Zone = None
        self.end: Zone = None
        self.size = 0
        self.drone_count = 0

    def add_zone(self, zone):
        self.zones[zone.name] = zone

    def add_connection(self,
                       first: Zone,
                       second: Zone,
                       capacity: int = 1):
        connection = Connection(first, second, capacity)
        first.connections.append(connection)
        second.connections.append(connection)

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
