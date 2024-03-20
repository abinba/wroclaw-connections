import math
from functools import lru_cache
from queue import PriorityQueue

from core.station import Station
from core.utils import OptimizationCriteria


@lru_cache(maxsize=None)
def euclidean_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    lat_dist = (lat2 - lat1) * 111139
    lon_dist = (lon2 - lon1) * 111139 * math.cos((lat1 + lat2) / 2)
    return math.sqrt(lat_dist**2 + lon_dist**2)


def shortest_path(
    graph: dict[str, Station],
    start_station: str,
    end_station: str,
    start_time: float,
    optimization: OptimizationCriteria = OptimizationCriteria.TIME.value,  # "time" | "transfer"
):
    pq = PriorityQueue()
    starting_estimated_cost = euclidean_distance(
        graph[start_station].location["lat"],
        graph[start_station].location["lon"],
        graph[end_station].location["lat"],
        graph[end_station].location["lon"],
    )
    pq.put((starting_estimated_cost, 0, start_station, None, start_time, [(start_station, start_time, "")]))

    visited = set()

    while not pq.empty():
        (
            estimated_total_cost, optimization_cost, current_station, previous_line_company, current_time, path
        ) = pq.get()

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
                            new_cost + euclidean_distance(
                                graph[next_station].location["lat"],
                                graph[next_station].location["lon"],
                                graph[end_station].location["lat"],
                                graph[end_station].location["lon"],
                            ),
                            new_cost,
                            next_station,
                            connection.line_company,
                            connection.arrival_time_minutes,
                            path + [(next_station, connection.arrival_time_minutes, connection.line_company)]
                        )
                    )
    return 0, []
