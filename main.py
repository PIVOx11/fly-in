from map_parser import Parser
from error_handling import ParsingError, SimulationError
import sys
from simulation import Simulation
# from src.display import GraphViewer

if __name__ == "__main__":
    from rich import print

    try:
        parse = Parser(sys.argv[1])
        graph = parse.generate_graph()
        sim = Simulation(graph) 
        sim.pivox_algo(3)
    except (ParsingError, SimulationError) as e:
        print(f"[red]{e}[/red]")
        exit(2)