import sys
from parser import Parser
from errors import ParsingError, MapError
from simulation import Simulation
from rich import print as over_print
from display import Display

if __name__ == "__main__":
    file: str

    if len(sys.argv) > 2:
        over_print("The program take only one argument ('Path to the map')")
        exit(1)

    if len(sys.argv) > 1:
        file = sys.argv[1]
    else:
        file = "maps/easy/01_linear_path.txt"

    try:
        parser = Parser()
        graph = parser.Graph_generator(file)
        sim = Simulation(graph)
        sim_data = sim.run()
        sim.output(sim_data)
        dispay = Display(sim_data, graph)
        dispay.run()

    except (ParsingError, MapError) as e:
        over_print(f"[red]{e}[/red]")
    except Exception:
        over_print("unexpected error")
