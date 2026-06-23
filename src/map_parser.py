

class Parsing_error(Exception):
    pass


class Parser:
    def __init__(self, file_path):
        map = {}
