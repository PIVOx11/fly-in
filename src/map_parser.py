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