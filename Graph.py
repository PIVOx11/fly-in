from __future__ import annotations
from typing import Any


class Zone:
    """
        Represents a hub or waypoint in the graph.
    """
    def __init__(
            self,
            name: str,
            x: int, y: int,
            line: int,
            connections: dict | None = None,
            color: str = "gray",
            zone_type: str = "normal",
            max_drones: int | float = 1
            ):
        """ Initialize The Zone obj"""
        self.name = name
        self.x = x
        self.y = y
        self.connections = connections or {}
        self.color = color
        self.max_drones = max_drones
        self.drones: list[Drone] = []
        self.zone_type = zone_type
        self.incoming = 0
        self.line = line

    def can_fitt(self) -> bool:
        """
            Return True if the zone capacity can accept a drone.
        """
        return self.incoming + len(self.drones) < self.max_drones

    def get_cost(self) -> int:
        """
            Return the movement cost of entering this zone.
        """
        if self.zone_type == "restricted":
            return 2
        return 1

    def get_connection(self, zone: Zone) -> Connection | None:
        """
            Return the connection to the given zone.
        """
        return self.connections.get(zone)

    def __repr__(self) -> str:
        """Define the representation of the Zone obj"""
        conect = []
        for c in self.connections.values():
            if c.first == self:
                conect.append(c.second.name)
            else:
                conect.append(c.first.name)
        return (
            f"===== Name: {self.name} ======"
            f"\nCordonates: {self.x, self.y}"
            f"\nConnectios: {conect}"
            f"\nDrones[{self.drones or 'empty'}]"
            f"\nCapacity: {self.max_drones}"
            f"\ncost: {self.get_cost()}\n"
            f"color: {self.color}\n"
            f"\nZone_type: {self.zone_type}\n"
        )


class Connection:
    """
        Represents a connection between two zones.
    """
    def __init__(
            self,
            first: Zone,
            second: Zone,
            capacity: int = 1
            ):
        """ Initialize The Connection obj"""
        self.first = first
        self.second = second
        self.capacity = capacity
        self.drones: list[Drone] = []
        self.incoming = 0
        self.active = True

    def can_delever(self) -> int:
        """
            Return True if another drone can enter the connection.
        """
        return len(self.drones) + self.incoming < self.capacity

    def other(self, zone: Zone) -> Zone:
        """
            Return the zone on the opposite of the connection.
        """
        if zone == self.first:
            return self.second
        return self.first

    def __repr__(self) -> str:
        """Define the representation of the Connection obj"""
        size = self.capacity
        return (f"{self.first.name} <---> {self.second.name} : "
                f"dron_capacity={size}")


class Graph:
    """
        Graph Class, to store zones and 
        connections and drones .
    """
    def __init__(self) -> None:
        """ Initialize The Graph obj"""
        self.drones: list[Drone] = []
        self.zones: dict = {}
        self.start: Zone | Any = None
        self.end: Zone | Any = None
        self.drone_count = 0

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph."""

        self.zones[zone.name] = zone

    def add_connection(self,
                       first: Zone,
                       second: Zone,
                       capacity: int = 1) -> None:
        """Create a connection between two zones."""

        connection = Connection(first, second, capacity)
        first.connections[second.name] = connection
        second.connections[first.name] = connection

    def is_over(self) -> bool:
        """
            Return True when all drones reach the destination.
        """

        return len(self.end.drones) >= self.drone_count

    def __repr__(self) -> str:
        """Define the representation of the Graph obj"""

        repr = [
            f"Start_hub:\n {self.start}",
            f"End_hub:\n {self.end}",
            "",
            "Zones:"
            ]

        for z in self.zones.values():
            repr.append(str(z))

        return "\n".join(repr)


class Drone:
    """Represents a drone moving through the graph."""
    def __init__(self, id: int) -> None:
        """ Initialize The Drone obj"""
        self.x: int = 0
        self.y: int = 0
        self.id: int = id
        self.path: list[Zone] = []
        self.index: int = 0
        self.to_arrive: int = 0
        self.finish: bool = False
        self.next_zone: Zone | Any = None
        self.curent_zone:  Zone | Any = None
        self.connect: Connection | Any

    def update_data(self, path: None | list[Zone] = None) -> None:
        """Update the drone's path and movement data."""

        if path:
            self.path = path

        self.curent_zone = self.path[self.index]

        if self.index >= len(self.path) - 1:
            return

        self.next_zone = self.path[self.index + 1]
        self.connect = self.curent_zone.connections[self.next_zone.name]

    def Execute_restricted(self) -> str:
        """Execute restricted Moves"""
        self.to_arrive -= 1

        if self.to_arrive == 1:
            self.connect.drones.append(self)
            self.connect.incoming -= 1
            return f"{self.curent_zone.name}-{self.next_zone.name}"
        else:
            self.connect.drones.remove(self)
            self.next_zone.incoming -= 1
            self.next_zone.drones.append(self)
            self.index += 1
            self.update_data()

            if self.index >= len(self.path) - 1:
                self.finish = True

        return self.curent_zone.name

    def Execute_move(self) -> str:
        """Move the drone to the next zone ."""

        self.next_zone.incoming -= 1
        self.connect.incoming -= 1
        self.index += 1
        self.next_zone.drones.append(self)

        self.update_data()
        if self.index >= len(self.path) - 1:
            self.finish = True

        return self.curent_zone.name

    def can_move(self) -> bool:
        """
            check if drone can move base on the Zone and connection capacity :)
        """
        if self.next_zone.can_fitt() and self.connect.can_delever():
            return True
        return False

    def __repr__(self) -> str:
        """Define the representation of the Drone obj"""
        return f"D{self.id}"
