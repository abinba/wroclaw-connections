import json

import pandas as pd

from config import CONSTRUCTED_GRAPH_FILE
from station import Station


class GraphManager:
    df: pd.DataFrame

    def set_df(self, df: pd.DataFrame):
        self.df = df

    def construct_graph(self):
        graph = {}
        for _, row in self.df.iterrows():
            start, end = row["start_stop"], row["end_stop"]

            if start not in graph:
                graph[start] = Station(
                    name=start,
                    location={
                        "lat": row["start_stop_lat"],
                        "lon": row["start_stop_lon"],
                    },
                )

            graph[start].add_connection(
                station=end,
                line=row["line"],
                company=row["company"],
                departure_time_minutes=row["departure_time_minutes"],
                arrival_time_minutes=row["arrival_time_minutes"],
                travel_time_minutes=row["travel_time_minutes"],
            )

        for station in graph:
            graph[station].sort_connections()

        self.save_graph(graph)
        return graph

    @staticmethod
    def save_graph(graph: dict[str, Station], filepath: str = CONSTRUCTED_GRAPH_FILE):
        for station in graph:
            graph[station] = graph[station].as_dict()

        with open(filepath, "w") as f:
            r = json.dumps(graph)
            f.write(r)

    @staticmethod
    def load_graph(filepath: str = CONSTRUCTED_GRAPH_FILE) -> dict | None:
        try:
            with open(filepath, "r") as f:
                graph = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

        for station in graph:
            graph[station] = Station.from_dict(graph[station])

        return graph
