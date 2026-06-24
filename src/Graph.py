class Graph:
    def __init__(self):
        zones: dict = {}

class Zone:
    def __int__(
            name: str, type: str, x: int, y: int,
            color: str | None = None, max_dron: int = 1,
            connections: list = []
            ):
        pass

class Connetion:
    def __init__(
            self, first: Zone, second: Zone, dron_capacity: int = 1
            ):
        pass