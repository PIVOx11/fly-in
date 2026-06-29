from src.map_parser import Parser
from src.error_handling import ParsingError, SimulationError
import sys
from src.simulation import Simulation
# from src.display import GraphViewer
if __name__ == "__main__":
    from rich import print

    try:
        parse = Parser(sys.argv[1])
        graph = parse.generate_graph()
        sim = Simulation(graph)
        sim.graph_validate()
    except (ParsingError, SimulationError) as e:
        print(f"[red]{e}[/red]")
        exit(2)
