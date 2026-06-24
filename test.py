from src.Graph import Graph, Connection, Zone


graph = Graph()

zone1 = Zone("hub1", "normal", 1, 1,
             color="red", max_dron=13)

zone2 = Zone("hub2", "normal", 2, 2,
             color="blue", max_dron=37)

graph.add_zone(zone1)
graph.add_zone(zone2)

graph.start = zone1
graph.end = zone2

graph.add_connection(zone1, zone2, 42)

print(graph)