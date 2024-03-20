import math
from functools import lru_cache
from queue import PriorityQueue
from typing import Literal

from core.station import Station
from core.utils import OptimizationCriteria


@lru_cache(maxsize=None)
def euclidean_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return math.sqrt(abs(lat2 - lat1) ** 2 + abs(lon2 - lon1) ** 2)


@lru_cache(maxsize=None)
def manhattan_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return abs(lat2 - lat1) ** 2 + abs(lon2 - lon1) ** 2


def heuristic(method: Literal["euclidean", "manhattan"]):
    if method == "euclidean":
        return euclidean_distance
    return manhattan_distance


def shortest_path(
    graph: dict[str, Station],
    start_station: str,
    end_station: str,
    start_time: float,
    optimization_criteria: OptimizationCriteria = OptimizationCriteria.TIME,
):
    pq = PriorityQueue()
    starting_estimated_cost = heuristic(method="manhattan")(
        graph[start_station].location["lat"],
        graph[start_station].location["lon"],
        graph[end_station].location["lat"],
        graph[end_station].location["lon"],
    )

    starting_cost = 0
    pq.put(
        (
            starting_estimated_cost,
            starting_cost,
            start_time,
            start_station,
            None,
            start_time,
            [(start_station, start_time)],
        )
    )

    visited = set()

    while not pq.empty():
        (
            estimated_total_cost,
            optimization_cost,
            _,
            current_station,
            previous_line_company,
            current_time,
            path,
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

                new_cost = optimization_cost
                new_estimated_cost = optimization_cost + heuristic(method="manhattan")(
                    graph[next_station].location["lat"],
                    graph[next_station].location["lon"],
                    graph[end_station].location["lat"],
                    graph[end_station].location["lon"],
                )

                for connection in connections:
                    waiting_time = connection.departure_time_minutes - current_time
                    new_estimated_cost += waiting_time + connection.travel_time_minutes
                    new_cost += waiting_time + connection.travel_time_minutes

                    if optimization_criteria == OptimizationCriteria.TRANSFER.value:
                        if previous_line_company != connection.line_company:
                            new_estimated_cost += 1
                            new_cost += 1

                    pq.put(
                        (
                            new_estimated_cost,
                            new_cost,
                            connection.departure_time_minutes,
                            next_station,
                            connection.line_company,
                            connection.arrival_time_minutes,
                            path
                            + [connection.line_company]
                            + [(next_station, connection.arrival_time_minutes)],
                        )
                    )
    return 0, []
