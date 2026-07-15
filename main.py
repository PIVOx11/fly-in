import sys
from parser import Parser
from error_handling import ParsingError, SimulationError
from simulation import Simulation
from display import Display
 
if __name__ == "__main__":
    from rich import print
 
    try:
        parser = Parser()
        graph = parser.Graph_generator(sys.argv[1])
        print(graph)
 
        sim = Simulation(graph)
        sim_data = sim.run()
        display = Display(graph, sim_data)
        display.run()
 
    except (ParsingError, SimulationError) as e:
        print(f"[red]{e}[/red]")
        exit(2)