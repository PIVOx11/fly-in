from errors import ParsingError, MapError
from Graph import Graph, Zone
from typing import Any
from typing import Callable
from simulation import Simulation


class Parser(Simulation):
    """
        Parser Class, parse and validate a given map file and return
        valid graph with zones and connections .
    """
    def __init__(self) -> None:
        """
            Create Graph obj (Graph()) and open map file
        """
        self.connections: set = set()
        self.con_To_create: list = []
        self.coordinates: set[tuple] = set()

    def save(self, line: str, index: int) -> None:
        """
            save Connections to handle at the end of file
        """
        self.con_To_create.append((line, index))

    def Graph_generator(self, map_path: str) -> Graph:
        """
            parse the map file and build a valid Graph obj
        """
        self.graph: Graph = Graph()
        line: Any

        handler: dict[str, Callable] = {
            "nb_drones": self.valid_drones_nb,
            "start_hub": self.valid_hub,
            "end_hub": self.valid_hub,
            "hub": self.valid_hub,
            "connection": self.save
        }

        self.comments = 0

        try:

            if not map_path.strip().endswith(".txt"):
                raise ParsingError(
                    "ERROR: Map file should be .txt format"
                )

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

                    if index - self.comments == 1 and line[0] != "nb_drones":
                        raise ParsingError(
                            f"Line {index}: first line should contain the 'nb_drones'"
                        )

                    if line[0] in handler:
                        handler[line[0]](line, index)
                    else:
                        raise ParsingError(
                            f"[italic]Line {index}: "
                            f"Unkown Key: [bold]'{line[0]}'[/bold]\n"
                            "Autorized Keys: [/italic][bold]"
                            f"{[key for key in handler]}[/bold]"
                        )

                for line, index in self.con_To_create:
                    self.valid_connection(line, index)
        except FileNotFoundError:
            raise ParsingError(
                f"Map file '{map_path}' not found."
            )
        except PermissionError:
            raise ParsingError(
                f"Permission denied while reading '{map_path}'. "
                "Check the file permissions."
            )
        except OSError:
            raise ParsingError(
                "ERROR: Cannot acsses To the gevin file ."
                "File given not a valid path, or not dir"
            )

        self.check()

        return self.graph

    def valid_drones_nb(self, line: list, index: int) -> None:
        """
            Method to validate the nb of drones argument .
        """
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
                    f"[italic]Line {index}: Drone numbers should be "
                    "Valide positive integer and (0 < nb_drones)\n"
                    "Example : [green][bold]nb_drones: 12"
                    "[/bold][/green][/italic]"
                )

            self.graph.drone_count = nb
        except ValueError:
            raise ParsingError(
                f"[italic]Line {index}: Drone numbers should be "
                "Valide positive integer (0 < nb_drones) \n"
                "Example : [green][bold]nb_drones: 12[/bold][/green][/italic]"
            )

    def valid_hub(self, line: str, index: int) -> None:
        """
            Method to valid Hubs and creat Zone obj .
        """
        data = line[1].split(maxsplit=3)
        metadata: Any
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
        zone = Zone(name, x, y, index)

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
            if self.graph.start:
                raise ParsingError(
                    f"Line{index}: start_hub is duplicated ."
                )

            self.graph.start = zone
            zone.max_drones = float("inf")

        if line[0] == "end_hub":
            if self.graph.end:
                raise ParsingError(
                    f"Line{index}: end_hub is duplicated ."
                )
            self.graph.end = zone
            zone.max_drones = float("inf")

        self.graph.add_zone(zone)

    def valid_name(self, name: str, index: int) -> str:
        """
            validate the name of given zone .
        """
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

    def valid_integer(self, nb: str | int, index: int) -> int:
        """
            Validate The integer's arguments
        """
        try:
            nb = int(nb)
        except ValueError:
            raise ParsingError(
                f"Line {index}: numbers should be valid positive integers \n"
            )
        return nb

    def valid_hub_metadata(self, metadata: Any, index: int) -> dict:
        """
            Method validate zones metadata fields
        """
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

            if key == "color":
                if value.isdigit():
                    raise ParsingError(
                        f"Line {index}: Color should be valid color "
                        "string not a number ."
                    )
            elif key == "max_drones":
                value = self.valid_integer(value, index)
                if value <= 0:
                    raise ParsingError(
                        f"Line {index}: Max_drone argument should be"
                        "should be valid positive integer ."
                    )
            elif key == "zone":
                if value not in zone_t:
                    raise ParsingError(f"Line {index}: Inkown zone type :)")

            found[key] = value

        return found

    def valid_connection(self, line: Any, index: int) -> None:
        """
            method to validate connection data
        """
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
            self, metadata: str, index: int) -> int:
        """
            Method to validate Connetctions metadata .
        """
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
            nb = self.valid_integer(value, index)
        except ValueError:
            raise ParsingError(
                f"Line {index}: Invalid metadata for Connection\n"
                "Exmaple : 'max_link_capacity=1'"
                )

        if nb <= 0:
            raise ParsingError(
                f"Line {index}: Max_link_capacity argument should be"
                " valid positive integer .")

        return nb

    def check(self) -> None:
        if not self.graph.start:
            raise ParsingError(
                "ERROR: No start zone included"
                )

        if self.graph.start.zone_type == "blocked":
            raise ParsingError(
                f"Line {self.graph.start.line}: "
                "Error Start Zone cannot be blocked ."
                )
        elif self.graph.end.zone_type == "blocked":
            raise ParsingError(
                f"Line {self.graph.end.line}: "
                "Error End Zone cannot be blocked ."
                )

        if not self.graph.end:
            raise ParsingError(
                "ERROR: No End zone included"
                )

        if not self.djikstra(self.graph.start, self.graph.end):
            raise MapError(
                "Error: theres No path between start zone and end Zone"
            )

        for zone in self.graph.zones.values():
            if not zone.connections:
                raise ParsingError(
                    f"ERROR: Zone={zone.name} is deconnected .\n"
                    "Evry Zone in map should be "
                    "connected with others .")

        self.map_validate()

    def map_validate(self) -> None:
        cach: set = set()
        path: Any = []

        for zone in self.graph.zones.values():

            if zone == self.graph.end:
                continue

            if zone in cach:
                continue

            path = self.bfs_search(zone, self.graph.end)

            if not path:
                s_zone = self.graph.zones[zone.name]
                raise MapError(
                    "ERROR: THe folowing Maps is Deconnected from the Graph: "
                    f"({s_zone.name} "
                    f"{' '.join([z for z in s_zone.connections])})"
                )

            for seen_zone, cost in path:
                zone = self.graph.zones[seen_zone]
                cach.add(zone)
