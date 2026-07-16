from error_handling import ParsingError
from Graph import Graph, Zone, Connection


class Parser:
    def __init__(self) -> None:
        """
            Create Graph obj (Graph()) and open map file
        """
        self.connections = set()
        self.con_To_create = []
        self.coordinates: set[tuple] = set()

    def save(self, line, index):
        self.con_To_create.append((line, index))

    def Graph_generator(self, map_path: str) -> Graph:
        self.graph = Graph()

        handler = {
            "nb_drones": self.valid_drones_nb,
            "start_hub": self.valid_hub,
            "end_hub": self.valid_hub,
            "hub": self.valid_hub,
            "connection": self.save
        }

        self.comments = 0
        try:
            with open(map_path, "r")as file:
                for index, line in enumerate(file, start=1):
                    line = line.strip()

                    if line.startswith("#"):
                        self.comments += 1
                        continue

                    if not line:
                        self.comments += 1
                        continue

                    line = line.split(":", 1)
                    line = [s.strip() for s in line]

                    if line[0] in handler:
                        handler[line[0]](line, index)
                    else:
                        raise ParsingError(
                            f"[italic]Line {index + self.comments}: "
                            f"Unkown Key: [bold]'{line[0]}'[/bold]\n"
                            "Autorized Keys: [/italic][bold]"
                            f"{[key for key in handler]}[/bold]"
                        )
                for line, index in self.con_To_create:
                    self.valid_connection(line, index)
        except FileNotFoundError:
            raise ParsingError(
                f"Map file '{map_path}' was not found."
            )
        except PermissionError:
            raise ParsingError(
                f"Permission denied while reading '{map_path}'. "
                "Check the file permissions."
            )
        self.check()
        return self.graph

    def valid_drones_nb(self, line: str, index: int) -> int | None:
        if self.graph.drone_count:
            raise ParsingError(
                f"Line {index}: Drone number Argument are duplicated.\n"
            )

        if index - self.comments > 1:
            raise ParsingError(
                f"[italic]line {index}: drone number, should be at the"
                "begening of the file :([/italic]"
            )

        line = line[1].split()

        if len(line) > 1:
            if not line[1].startswith("#"):
                raise ParsingError(
                    f"[italic]Line {index}: Wrong Line Format\n"
                    "Example : [green][bold]nb_drones: 12[/bold]"
                    "[/green][/italic]"
                )
        try:
            nb = int(line[0])
            if nb <= 0:
                raise ParsingError(
                    f"[italic]Line {index}: Drone number should be "
                    "Valide positive integer\n"
                    "Example : [green][bold]nb_drones: 12"
                    "[/bold][/green][/italic]"
                )
            self.graph.drone_count = nb
        except ValueError:
            raise ParsingError(
                f"[italic]Line {index}: Drone number should be "
                "Valide positive integer\n"
                "Example : [green][bold]nb_drones: 12[/bold][/green][/italic]"
            )

    def valid_hub(self, line: str, index: int) -> Zone:
        data = line[1].split(maxsplit=3)

        if len(data) < 3:
            raise ParsingError(
                f"Line {index}: Line format error\n"
                "Example [green]hub: gate1 1 0 "
                "[bold][color=orange max_drones=1][/green][/bold]"
            )

        name, x, y, metadata = self.valid_name(data[0], index), \
            self.valid_integer(data[1], index), \
            self.valid_integer(data[2], index), data[3] \
            if len(data) > 3 else None

        if name in self.graph.zones:
            raise ParsingError(
                f"Line {index}: Zone name is Duplicated :)"
                )

        if (x, y) in self.coordinates:
            raise ParsingError(f"Line {index} duplicated conrdonates {x, y}")
        self.coordinates.add((x, y))
        zone = Zone(name, x, y)

        if metadata and not metadata.strip().startswith('#'):
            metadata = self.valid_hub_metadata(metadata, index)
            for k, v in metadata.items():
                if k == "max_drones":
                    zone.max_drones = v
                elif k == "zone":
                    zone.zone_type = v
                elif k == "color":
                    zone.color = v.upper()

        if line[0] == "start_hub":
            self.graph.start = zone
            zone.max_drones = float("inf")

        if line[0] == "end_hub":
            self.graph.end = zone
            zone.max_drones = float("inf")

        self.graph.add_zone(zone)

    def valid_name(self, name: str, index: int) -> str:
        if "-" in name:
            raise ParsingError(
                f"Line {index}: Wrong Name format, name "
                "shouldn't include '-'\n"
            )

        if name in self.graph.zones:
            raise ParsingError(
                f"Line {index}: Zone name are duplacted, "
                "zones name should be unique :)\n"
            )

        return name

    def valid_integer(self, nb: str, index: int) -> int:
        try:
            nb = int(nb)
        except ValueError:
            raise ParsingError(
                f"Line {index}: numbers should be valid positive integers \n"
            )
        return nb

    def valid_hub_metadata(self, metadata: str, index: int) -> dict:
        AUTHO = {"max_drones", "zone", "color"}
        zone_t = {"normal", "blocked", "restricted", "priority"}
        found = {}

        if not metadata.startswith('[') or not metadata.endswith(']'):
            raise ParsingError(
                f"Line {index}: metadata should be inside squre brackets :)"
            )
        metadata = metadata.removeprefix('[').removesuffix(']').strip().split()
        if not metadata:
            raise ParsingError(f"Line {index}: Metadata is empty")
        for data in metadata:
            try:
                key, value = data.split('=')
            except ValueError:
                raise ParsingError(
                    f"Line {index}: Invalid metadata Argument\n"
                    "exanple: key=value"
                )
            if not value:
                raise ParsingError(
                    f"Line {index}: Empty value {key}=''"
                    )

            if key not in AUTHO:
                raise ParsingError(
                    f"Line {index}: Unkown key '{key}'\n"
                    f"Authorized keys {AUTHO}")

            if key in found:
                raise ParsingError(f"Line {index}: key {key} is duplacated")

            if key == "max_drones":
                value = self.valid_integer(value, index)
                if value <= 0:
                    raise ParsingError(
                        f"Line {index}: Max_drone argument should be"
                        "should be valid positive integer .")
            elif key == "zone":
                if value not in zone_t:
                    raise ParsingError(f"Line {index}: Inkown zone type :)")
            found[key] = value

        return found

    def valid_connection(self, line: str, index: int) -> Connection:
        max_link = 1
        line = line[1].split()
        zones, metadata = line[0], line[1] if len(line) > 1 else None

        if metadata and metadata.startswith('#'):
            metadata = None

        try:
            zone_1, zone_2 = zones.split("-")
        except ValueError:
            raise ParsingError(
                f"Line {index}: Invalid Connection format between "
                f"zones '{zones}'\n"
                "Example: <zone1>-<zone2> | (gate1-waiting_area1)")
        if zone_1 == zone_2:
            raise ParsingError(
                            f"Line {index}: Connection between "
                            f"The same zone is forbiden, {zone_1}-{zone_2}"
                        )
        if zone_1 not in self.graph.zones:
            raise ParsingError(
                f"Line {index}: Zone {zone_1} Not Found"
            )
        elif zone_2 not in self.graph.zones:
            raise ParsingError(
                f"Line {index}: Zone {zone_2} Not Found"
            )

        if metadata:
            max_link = self.valid_connections_metadata(metadata, index)

        connection = tuple(sorted((zone_1, zone_2)))
        if connection in self.connections:
            raise ParsingError(
                f"Line {index}: connection {zone_1}-{zone_2} is duplicated"
                )
        self.connections.add(connection)

        zone_1, zone_2 = self.graph.zones[zone_1], \
            self.graph.zones[zone_2]

        self.graph.add_connection(zone_1, zone_2, max_link)

    def valid_connections_metadata(
            self, metadata: str, index: int) -> int | None:
        AUTHO = {"max_link_capacity"}

        if not metadata.startswith('[') or not metadata.endswith(']'):
            raise ParsingError(
                f"Line {index}: Metadata should include "
                "inside squire brackets '[]'"
            )

        metadata = metadata.removeprefix('[').removesuffix(']').strip()

        try:
            key, value = metadata.split("=")
            if key not in AUTHO:
                raise ParsingError(
                    f"Line {index}: Wrong metadata <{key}> "
                    "connection accept only Max_link_capacity .")
            value = self.valid_integer(value, index)
        except ValueError:
            raise ParsingError(
                f"Line {index}: Invalid metadata for Connection\n"
                "Exmaple : 'max_link_capacity=1'"
                )

        if value <= 0:
            raise ParsingError(
                f"Line {index}: Max_link_capacity argument should be"
                " valid positive integer .")

        return value

    def check(self):
        if not self.graph.start:
            raise ParsingError(
                "ERROR: No start zone included"
                )

        if not self.graph.end:
            raise ParsingError(
                "ERROR: No End zone included"
                )

        for zone in self.graph.zones.values():
            if not zone.connections:
                raise ParsingError(
                    f"ERROR: Zone '{zone.name}' is deconnected .\n"
                    "Evry Zone in map should be "
                    "connected with others .")
