from .error_handling import ParsingError


class Parser:
    def __init__(self, file_path):
        try:
            self.file = open(file_path, "r")
        except FileNotFoundError:
            raise ParsingError("The specified file was not found.")
        except PermissionError:
            raise ParsingError("Permission denied while opening the file.")
        except Exception:
            raise ParsingError("An unexpected error occurred while opening the file.")

    def data_validate(self) -> dict:
        lines = 1 # Lines Counter
        comment = 0 # how many line are ignored
        data = {}
        
        for line in self.file:
            line = line.strip()

            if line.startswith("#") or not line:
                comment += 1
                continue
            line = line.split(":")
            if line[0] == "nb_drones":
                if lines != 1:
                    raise ParsingError(f"Line {lines + comment}: "\
                                        "Number of drones not at the begenning of the file :)")
                data["drone_n"] = self.drone_nb_parser(line, lines)
            elif lines > 1 and not data.get("drone_n"):
                raise ParsingError("Number of drones not at the begenning of the file :)")

            yield line
            lines += 1

    def drone_nb_parser(self, line: list[str], lines: int) -> int:
        if len(line) < 2:
             raise ParsingError(f"Line {lines}: "\
                                 "Number of drones invalide or missing :(")
        number = line[1]
        try:
            number = int(number)    
        except Exception:
            raise ParsingError(f"Line {lines}: "\
                                 "Number of drones invalide or missing :(")
        if number < 0:
                raise ParsingError(f"Line {lines}: "\
                                    "Number of drones invalid cannot be zero or negative :(")
        return number

        







# if line.strip().startswith("start_hub") or\
#     line.strip().startswith("start_hub"):
#     pass
# elif line.strip().startswith("hub"):
#     pass
# elif line.strip().startswith("connection"):
#     pass
# else:
#     pass