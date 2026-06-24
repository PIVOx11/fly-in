
class Zone:
    def __init__(
            self,
            name: str,
            zone_type: str,
            x: int, y: int,
            connections: list | None = None,
            color: str | None = None,
            max_dron: int = 1
            ):
        self.name = name
        self.zone_type = zone_type
        self.x = x
        self.y = y
        self.connections = connections or []
        self.color = color
        self.max_dron = max_dron

    def __repr__(self):
        conect = []
        for c in self.connections:
            if c.first == self:
                conect.append(c.second.name)
            else:
                conect.append(c.first.name)                
        return (
            f"Name: {self.name}"
            f" Type: {self.zone_type}"
            f" Connectios: {conect}"
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
        return f"{self.first.name} <---> {self.second.name} : dron_capacity={size}"


class Graph:
    def __init__(self):
        self.zones: dict = {}
        self.start: Zone = None
        self.end: Zone = None

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
            f"Start: {self.start.name or 'None'}",
            f"End: {self.end.name or 'None'}",
            "",
            "Zones:"
            ]
        for z in self.zones.values():
            repr.append(str(z))
        return "\n".join(repr)
