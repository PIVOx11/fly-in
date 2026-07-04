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
        # print(graph)
        # exit()
        sim = Simulation(graph)
        sim.run()
        # print(sim.djikstra(graph.start, graph.end))
        # print(sim.bfs_search(graph.start, graph.end))
    except (ParsingError, SimulationError) as e:
        print(f"[red]{e}[/red]")
        exit(2)