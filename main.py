import sys
from parser import Parser
from error_handling import ParsingError, SimulationError
from simulation import Simulation
from display import Display
from rich import print as over_print


if __name__ == "__main__":
    file: str

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
        # display = Display(sim_data, graph)
        # display.run()

    except (ParsingError, SimulationError) as e:
        over_print(f"[red]{e}[/red]")
