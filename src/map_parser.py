from .error_handling import ParsingError
from .Graph import Graph, Zone, Connection, Drone

class Parser:
    def __init__(self, file_path):
        """
            Create Graph obj (Graph()) and open map file 
        """
        self.data = {}
        self.graph = Graph()
        self.connections = []
        self.line_counter = 0
        self.coordinates: list[tuple] = []

        try:
            self.file = open(file_path, "r")
        except FileNotFoundError:
            raise ParsingError("The specified file was not found.")
        except PermissionError:
            raise ParsingError("Permission denied while opening the file.")
        except Exception:
            raise ParsingError("An unexpected error occurred while opening the file.")

    def generate_graph(self) -> Graph:
        """
            Generate Graph by parsing map file 
        """
        comment = 0

        for line_c, line in enumerate(self.file, start=1):
            self.line_counter = line_c
            line = line.strip()

            if line.startswith("#") or not line:
                comment += 1
                continue
            if line_c - comment > 1 and "nb_drones" not in self.data:
                raise ParsingError("Number of drones not at the begenning of the file :)")
            line = line.split(":")

            if line[0] == "nb_drones":
                self.data["nb_drones"] = self.drone_nb_parser(line, line_c, comment)
            elif line[0] == "start_hub" or\
                 line[0] == "end_hub" or line[0] == "hub":
                self.hubs_parser(line, line_c)
            elif line[0] == "connection":
                pass
            else:
                raise ParsingError(f"Line {line_c} Unknown Key Argument '{line[0]}'")
        return self.graph

    def drone_nb_parser(self, line: list[str], line_c: int, comment: int) -> int:
        """
            Parse and Validate The number of drones given and,
            raise parsing error if it invalid like: (0, -[/d+], char, ...) .
        """
        if self.data.get("nb_drones"):
            raise ParsingError(f"Line {line_c + comment}: "\
                                 "Number of drones are Duplacated")
        line_c += comment
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
                                    "Number of drones invalid cannot be zero or negative :(")
        return number

    def hubs_parser(self, line: list[str], line_c: int) -> None:
        if len(line) != 2:
            raise ParsingError(f"Line {line_c}: Invalid Line .")
        arg = line[1].strip().split(" ", 3)
        print(arg , len(arg))
        if len(arg) not in (3, 4):
            raise ParsingError(f"Line {line_c}: Data Counte Invalide .")
        name, x, y, metadata = arg[0], arg[1], arg[2], None if len(arg) == 3 else arg[3]
        name = self.name_check(name)
        cord = self.cordonate_validation(x, y)
        zone = Zone(name=name, x=x, y=y)
        self.graph.add_zone(zone)

    def name_check(self, name: str) -> str:
        name = name.strip()
        if name in self.graph.zones:
            raise ParsingError(f"Line {self.line_counter}: "\
                                "Zone Name are duplecate .")
        if name.isdigit():
            raise ParsingError(f"Line {self.line_counter}: "\
                                "Zone Name Contain only digits"\
                                f", example('_path1', 'maze_1') are valid but {name} NOT .")
        if "-" in name:
            raise ParsingError(f"Line {self.line_counter}: "\
                                "Zone Name Contain Dash '-'"\
                                f" , example('path1', 'maze_1') are valid but {name} NOT .")
        return name

    def cordonate_validation(self, x: int, y: int) -> tuple:
        try:
            x = int(x)
            y = int(y)
        except ValueError:
            raise ParsingError(f"Line {self.line_counter}: "\
                               "Invalid Conrdonate Should be valid integers .")
        if (cord:=(x, y)) in self.coordinates:
            raise ParsingError(f"Line {self.line_counter}: Coordinates duplecated {cord}.")
        self.coordinates.append(cord)
        return cord

    def parse_metadata(self, metadata: list[str], zone: Zone):
        pass # To do






###             FILE EXAMPLE :              ###


# # Easy Level 2: Simple fork with two paths
# nb_drones: 4

# start_hub: start 0 0 [color=green]
# hub: junction 1 0 [color=yellow max_drones=2]
# hub: path_a 2 1 [color=blue]
# hub: path_b 2 -1 [color=blue]
# end_hub: goal 3 0 [color=red max_drones=3]

# connection: start-junction [max_link_capacity=2]
# connection: junction-path_a
# connection: junction-path_b
# connection: path_a-goal
# connection: path_b-goal


# chnage the shitty if .. with calleble method's
# handlers = {
#     "nb_drones": self.drone_nb_parser,
#     "hub": self.hubs_parser,
#     "start_hub": self.hubs_parser,
#     "end_hub": self.hubs_parser,
#     "connection": self.connection_parser,
# }