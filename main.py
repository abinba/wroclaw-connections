import time

import pandas as pd

from algorithms import djikstra, astar
from algorithms.djikstra import OptimizationCriteria
from config import CONNECTION_GRAPH_FILE
from core.graph import GraphManager
from core.utils import time_to_minutes, minutes_to_time, format_path


def get_df() -> pd.DataFrame:
    """
    connection_graph.csv is a csv file with information about connections between stops in Wroclaw.

    Fields in the csv file:
        id: int
        company: str, example: MPK Autobusy
        line: str, example: "1"
        departure_time: str, example: "05:00:00"
        arrival_time: str, example: "05:10:00"
        start_stop: name of the start stop
        end_stop: name of the end stop
        start_stop_lat: float
        start_stop_lon: float
        end_stop_lat: float
        end_stop_lon: float

    :return: pd.DataFrame with 3 additional columns:
        - travel_time_minutes: float
        - departure_time_minutes: float
        - arrival_time_minutes: float
    """
    column_types = {"line": str}
    df = pd.read_csv(CONNECTION_GRAPH_FILE, dtype=column_types)
    df["travel_time_minutes"] = df.apply(
        lambda row: time_to_minutes(row["arrival_time"])
        - time_to_minutes(row["departure_time"]),
        axis=1,
    )
    df["departure_time_minutes"] = df["departure_time"].apply(time_to_minutes)
    df["arrival_time_minutes"] = df["arrival_time"].apply(time_to_minutes)
    return df


if __name__ == "__main__":
    graph_manager = GraphManager()
    graph = graph_manager.load_graph()

    if graph is None:
        print("Graph file not found, constructing graph...")
        df = get_df()
        graph_manager.set_df(df)
        graph = graph_manager.construct_graph()
        print("Graph constructed and saved!")
    else:
        print("Graph loaded!")

    # Dijkstra's algorithm
    print("\nDijkstra's algorithm")
    s = time.time()
    travel_time, path = djikstra.shortest_path(
        graph=graph,
        start_station="BISKUPIN",
        end_station="KRZYKI",
        start_time=800,
        optimization=OptimizationCriteria.TIME.value,
    )
    print(f"Execution time: {time.time() - s:.4f} seconds")
    print(travel_time)
    print(format_path(path))

    # A* algorithm
    print("\nA* algorithm optimized for transfer")
    s = time.time()
    transfers, path = astar.shortest_path(
        graph=graph,
        start_station="BISKUPIN",
        end_station="KRZYKI",
        start_time=800,
        optimization=OptimizationCriteria.TIME.value,
    )
    print(f"Execution time: {time.time() - s:.4f} seconds")
    print(transfers)
    print(format_path(path))
