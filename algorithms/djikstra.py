from enum import Enum
from queue import PriorityQueue

from core.station import Station


class OptimizationCriteria(Enum):
    TIME = "time"
    TRANSFER = "transfer"


def shortest_path(
    graph: dict[str, Station],
    start_station: str,
    end_station: str,
    start_time: float,
    optimization: OptimizationCriteria = OptimizationCriteria.TIME.value,  # "time" | "transfer"
):
    pq = PriorityQueue()

    pq.put((0, start_station, None, start_time, [(start_station, start_time, "")]))

    visited = set()

    while not pq.empty():
        optimization_cost, current_station, previous_line_company, current_time, path = pq.get()

        if current_station in visited:
            continue

        visited.add(current_station)

        if current_station == end_station:
            return optimization_cost, path

        if current_station:
            station = graph[current_station]

            # Going over all the available edges
            for next_station in station.connections:
                if next_station in visited:
                    continue

                connections = station.find_connections(
                    next_station,
                    current_time,
                    previous_line_company,
                )

                if not connections:
                    continue

                for connection in connections:
                    if optimization == OptimizationCriteria.TRANSFER.value:
                        if (
                            previous_line_company is not None and  # if it's not the first station
                            connection.line_company != previous_line_company
                        ):
                            new_cost = optimization_cost + 1
                        else:
                            new_cost = optimization_cost
                    else:
                        waiting_time = connection.departure_time_minutes - current_time
                        new_cost = (
                            optimization_cost + waiting_time + connection.travel_time_minutes
                        )

                    pq.put(
                        (
                            new_cost,
                            next_station,
                            connection.line_company,
                            connection.arrival_time_minutes,
                            path + [(next_station, connection.arrival_time_minutes, connection.line_company)]
                        )
                    )
    return 0, []
