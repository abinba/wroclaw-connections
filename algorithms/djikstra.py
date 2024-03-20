from dataclasses import dataclass
from queue import PriorityQueue

from core.station import Station
from core.utils import minutes_to_time


class PathConnection:
    def __init__(
        self,
        current_station: str,
        arrival_time: float,
        line_company: str,
    ):
        self.current_station = current_station
        self.arrival_time = arrival_time
        self.line_company = line_company

    def __str__(self):
        return f"{self.current_station} ({minutes_to_time(self.arrival_time)}) ({self.line_company})"


@dataclass(order=True)
class Metadata:
    current_station: str
    current_time: float
    previous_line_company: str
    path: list[PathConnection]

    def __init__(
        self,
        current_station: str,
        current_time: float,
        previous_line_company: str,
        path: list[PathConnection],
    ):
        self.current_station = current_station
        self.current_time = current_time
        self.previous_line_company = previous_line_company
        self.path = path

    def __str__(self):
        path = " -> ".join([str(p) for p in self.path])
        return (
            f"Station: {self.current_station}, Time: {self.current_time}\nPath: {path}"
        )


def shortest_path(
    graph: dict[str, Station],
    start_station: str,
    end_station: str,
    start_time: float,
    time_optimization: bool = False,
    transfer_optimization: bool = False,
):
    pq = PriorityQueue()

    path = PathConnection(
        current_station=start_station,
        arrival_time=start_time,
        line_company="",
    )

    metadata = Metadata(
        current_station=start_station,
        current_time=start_time,
        previous_line_company="",
        path=[path],
    )

    pq.put((0, metadata))

    visited = set()

    while not pq.empty():
        current_time_cost, metadata = pq.get()
        current_station = metadata.current_station

        if current_station in visited:
            continue

        visited.add(current_station)

        if current_station == end_station:
            return current_time_cost, metadata.path

        if current_station:
            station = graph[current_station]

            # Going over all the available edges
            for next_station in station.connections:
                if next_station in visited:
                    continue

                connection = station.find_connection(
                    next_station,
                    metadata.current_time,
                    metadata.previous_line_company,
                )

                if not connection:
                    continue

                waiting_time = connection.departure_time_minutes - metadata.current_time
                new_cost = (
                    current_time_cost + waiting_time + connection.travel_time_minutes
                )

                path = PathConnection(
                    current_station=next_station,
                    arrival_time=connection.arrival_time_minutes,
                    line_company=connection.line_company,
                )

                metadata = Metadata(
                    current_station=next_station,
                    current_time=connection.arrival_time_minutes,
                    previous_line_company=connection.line_company,
                    path=metadata.path + [path],
                )

                pq.put((new_cost, metadata))
    return 0, []
