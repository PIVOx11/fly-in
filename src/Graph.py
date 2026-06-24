class Graph:
    def __init__(self):
        zones: dict = {}
        start: Zone = None
        end: Zone = None

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
        conect = [zone.name for zone in self.conections]
        return f"{self.name}: {conect or 'No connections'}"


class Connetion:
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
        return f"{self.first} ===> {self.second} : dron_capacity={size}"