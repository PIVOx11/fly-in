from src.map_parser import Parser
from src.error_handling import ParsingError
import sys


if __name__ == "__main__":
    from rich import print
    try:
        parse = Parser(sys.argv[1])
    except ParsingError as e:
        print(f"[red]{e}[/red]")
    try:
        for i in parse.data_validate():
            print(f"[green] {i}[/green]")
    except ParsingError as e:
        print(f"[red]{e}[/red]")

    
    # Now need to parse the data inside file :)