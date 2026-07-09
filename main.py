from map_parser import Parser
from error_handling import ParsingError, SimulationError
import sys
from simulation import Simulation



if __name__ == "__main__":
    from rich import print

    try:
        parse = Parser(sys.argv[1])
        graph = parse.generate_graph()
        sim = Simulation(graph)
        # print(sim.pivox_algo(20)) 
        for path in sim.drone_path():
            print(path)
    except (ParsingError, SimulationError) as e:
        print(f"[red]{e}[/red]")
        exit(2)
