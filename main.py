import sys
from map_parser import Parser
from error_handling import ParsingError, SimulationError
from simulation import Simulation
from display import Display
from tools.arcade_visualizer import DroneVisualizerApp
 
if __name__ == "__main__":
    from rich import print
 
    try:
        parse = Parser(sys.argv[1])
        graph = parse.generate_graph()
 
        sim = Simulation(graph)
        sim_data = sim.run()
        display = Display(graph, sim_data)
        display.run()
 
    except (ParsingError, SimulationError) as e:
        print(f"[red]{e}[/red]")
        exit(2)