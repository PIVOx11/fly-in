from src.map_parser import Parser
from src.error_handling import ParsingError
import sys


if __name__ == "__main__":
    from rich import print
    try:
        parse = Parser(sys.argv[1])
    except ParsingError as e:
        print(f"[red]{e}[/red]")
        exit(2)
    try:
        parse.generate_graph()
        print(parse.graph)
    except ParsingError as e:
        print(f"[red]{e}[/red]")
        exit(2)

    
    # Now need to parse the data inside file :)