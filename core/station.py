from collections import defaultdict
from typing import Optional

from config import MIN_TRANSFER_TIME
from connection import Connection


class Station:
    def __init__(
        self, name: str, location: dict, connections: dict[str, list[Connection]] = None
    ):
        self.name = name
        self.location = location

        if connections is None:
            self.connections: dict[str, list[Connection]] = defaultdict(list)
        else:
            self.connections = connections

    def add_connection(
        self,
        station: str,
        line: str,
        company: str,
        departure_time_minutes: float,
        arrival_time_minutes: float,
        travel_time_minutes: float,
    ):
        connection = Connection(
            line=line,
            company=company,
            departure_time_minutes=departure_time_minutes,
            arrival_time_minutes=arrival_time_minutes,
            travel_time_minutes=travel_time_minutes,
        )
        self.connections[station].append(connection)

    def sort_connections(self):
        for station in self.connections:
            self.connections[station].sort(key=lambda x: x.departure_time_minutes)

    def find_connection(
        self,
        next_station: str,
        current_time: float,
        previous_line_company: str = None,
    ) -> Optional[Connection]:
        """
        Find the next connection to the next station from the current station.
        Uses binary search within departure times of available connections to find the next connection.

        :param next_station: str
        :param current_time: float
        :param previous_line_company: str
        :return: Connection | None
        """
        connections_to_next_station: list[Connection] = self.connections[next_station]

        left, right = 0, len(connections_to_next_station) - 1
        target_position = len(connections_to_next_station) - 1

        while left <= right:
            mid = left + (right - left) // 2
            if connections_to_next_station[mid].departure_time_minutes < current_time:
                left = mid + 1
            else:
                target_position = mid
                right = mid - 1

        suitable_connections = []
        for i in range(
            target_position,
            min(target_position + 10, len(connections_to_next_station) - 1),
        ):
            # Prioritize connections with the same line as the previous one
            if (
                previous_line_company
                and connections_to_next_station[i].line_company == previous_line_company
            ):
                return connections_to_next_station[i]
            else:
                # If the connection is too close to the current time, skip it
                if (
                    connections_to_next_station[i].departure_time_minutes - current_time
                    < MIN_TRANSFER_TIME
                ):
                    continue
            suitable_connections.append(connections_to_next_station[i])

        if suitable_connections:
            return suitable_connections[0]

        return None

    def as_dict(self):
        return {
            "name": self.name,
            "location": self.location,
            "connections": {
                station: [c.__dict__ for c in self.connections[station]]
                for station in self.connections
            },
        }

    @classmethod
    def from_dict(cls, d: dict):
        connections = {}

        for station in d["connections"]:
            connections[station] = [Connection(**c) for c in d["connections"][station]]

        return cls(
            name=d["name"],
            location=d["location"],
            connections=connections,
        )

    def __str__(self):
        return f"Station({self.name})"
