from .error_handling import ParsingError
from .Graph import Graph, Zone, Connection, Drone


class Parser:
    def __init__(self, file_path):
        """
            Create Graph obj (Graph()) and open map file 
        """
        self.graph = Graph()
        self.connections = []
        self.coordinates: list[tuple] = []

        try:
            self.file = open(file_path, "r")
        except FileNotFoundError:
            raise ParsingError("The specified file was not found.")
        except PermissionError:
            raise ParsingError("Permission denied while opening the file.")
        except Exception:
            raise ParsingError("An unexpected error "\
                               "occurred while opening the file.")

    def generate_graph(self) -> Graph:
        """
            Generate Graph by parsing map file .
        """
        comment = 0
        handlers = {
            "nb_drones": self.drone_nb_parser,
            "hub": self.hubs_parser,
            "start_hub": self.hubs_parser,
            "end_hub": self.hubs_parser
        }

        for line_c, line in enumerate(self.file, start=1):
            line = line.strip()

            if line.startswith("#") or not line:
                comment += 1
                continue

            line = line.split(":")

            if line_c - comment > 1 and not self.graph.drone_count:
                raise ParsingError("dron_nb not At the begenning of the file .")
            if line[0] in handlers:
                handlers[line[0]](line, line_c)
            # else:
            #     raise ParsingError(f"Line {line_c} Unknown Key Argument '{line[0]}'")

            comment += 1

        self.file.close()
        return self.graph

    def drone_nb_parser(self, line: list[str], line_c: int) -> None:
        """
            Parse and Validate The number of drones given and,
            raise parsing error if it invalid like: (0, -[/d+], char, ...) .
        """
        if self.graph.drone_count:
            raise ParsingError(f"Line {line_c}: "\
                                 "Number of drones are Duplacated")
        if len(line) != 2:
             raise ParsingError(f"Line {line_c}: "\
                                 "Number of drones Invalide or missing :(")
        number = line[1]
        try:
            number = int(number)
        except ValueError:
            raise ParsingError(f"Line {line_c}: "\
                                 "Number of drones invalide or missing :(")
        if number <= 0:
                raise ParsingError(f"Line {line_c}: "\
                                    "Number of drones invalid cannot "\
                                    "be zero or negative :(")
        self.graph.drone_count = number
        return

    def hubs_parser(self, line: list[str], line_c: int) -> None:
        if len(line) != 2:
            raise ParsingError(f"Line {line_c}: Invalid Line .")

        if line[0] == "start_hub":
            if self.graph.start:
                raise ParsingError(f"Line {line_c}: Start_hub are duplacated, "\
                                   "Should be only one start_hub and end_hub .")
        elif line[0] == "end_hub":
            if self.graph.end:
                raise ParsingError(f"Line {line_c}: End_hub are duplacated, "\
                                   "Should be only one start_hub and end_hub .")

        arg = line[1].strip().split(" ", 3)
        if len(arg) not in (3, 4):
            raise ParsingError(f"Line {line_c}: Data Counte Invalide .")
        name, x, y, metadata = arg[0], arg[1], arg[2], None if len(arg) == 3 else arg[3]
        name = self.name_check(name, line_c)
        x, y = self.cordonate_validation(x, y, line_c)
        zone = Zone(name=name, x=x, y=y)
        self.graph.add_zone(zone)
        self.parse_metadata(metadata, zone, line_c)
        if line[0] == "start_hub":
            self.graph.start = zone
        elif line[0] == "end_hub":
            self.graph.end = zone
        
    def name_check(self, name: str, line_c: int) -> str:
        name = name.strip()
        if name in self.graph.zones:
            raise ParsingError(f"Line {line_c}: "\
                                "Zone Name are duplecate .")
        if name.isdigit():
            raise ParsingError(f"Line {line_c}: "\
                                "Zone Name Contain only digits"\
                                f", example('_path1', 'maze_1') are valid but {name} NOT .")
        if "-" in name:
            raise ParsingError(f"Line {line_c}: "\
                                "Zone Name Contain Dash '-'"\
                                f" , example('path1', 'maze_1') are valid but {name} NOT .")
        return name

    def cordonate_validation(self, x: int, y: int, line_c: int) -> tuple:
        try:
            x = int(x)
            y = int(y)
        except ValueError:
            raise ParsingError(f"Line {line_c}: "\
                               "Invalid Conrdonate Should be valid integers .")
        if (cord:=(x, y)) in self.coordinates:
            raise ParsingError(f"Line {line_c}: Coordinates duplecated {cord}.")
        self.coordinates.append(cord)
        return cord

    def parse_metadata(self, metadata: str, zone: Zone, line_c: int):
        if not metadata:
            zone.color = "LATER"
            zone.zone_type = "normal"
            return
        allowed_data = {
            "zone": {"normal", "priority", "restricted", "blocked"},
            "color": None,
            "max_drones": 1
        }
        data = {

        }

        metadata = metadata.strip()
        if not metadata.startswith("[") or not metadata.endswith("]"):
            raise ParsingError(f"Line {line_c}: metadata invalid should " \
                               "be inside \[metadata] .")
        metadata = metadata.removeprefix("[").removesuffix("]").strip()
        metadata = metadata.split()

        try:
            for string in metadata:
                k, v = string.split("=", 1)
                if not v:
                    raise ParsingError(f"Line {line_c}: "\
                                       f"Value of the {k} is empty")
                if k in allowed_data:
                    if k in data:
                        raise ParsingError(f"Line {line_c}: duplacated Data '{k}' .")
                    if k == "zone" and v not in allowed_data[k]:
                        raise ParsingError(f"Line {line_c}: "\
                                           f"Unkown Zone type '{v}', allowed Zonetypes: "\
                                           f"({', '.join(allowed_data[k])}) .")
                    if k == "max_drones":
                        if v.isdigit():
                            v = int(v)
                            if v <= 0:
                                raise ParsingError(f"Line {line_c}: "\
                                                   f"Max dron Should be valid integer (1-45).")    
                        else:
                            raise ParsingError(f"Line {line_c}: "\
                                               f"Max dron Should be valid integer (1-45).")
                else:
                    raise ParsingError(f"Line {line_c}: "\
                                        f"Unkown key type '{k}', allowed data: \n"\
                                        f"({', '.join(allowed_data)}) .")
                data[k] = v
        except ValueError as e:
            raise ParsingError(f"Line {line_c}: "\
                               "Unkown Argument Fromat, exmple: \[color=black] ...")
        zone.color = data.get("color", None)
        zone.max_drones = int(data.get("max_drones", 1))
        zone.zone_type = data.get("zone", "normal")
    def set_default_arg(self, zone: Zone):
        pass
