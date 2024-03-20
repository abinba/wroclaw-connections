from enum import Enum


def time_to_minutes(time_str: str):
    h, m, s = map(int, time_str.split(":"))
    return h * 60 + m + s / 60.0


def minutes_to_time(minutes: float):
    h = int(minutes // 60)
    m = int(minutes % 60)
    s = int((minutes - int(minutes)) * 60)
    return f"{h}:{m}:{s}"


class OptimizationCriteria(Enum):
    TIME = "time"
    TRANSFER = "transfer"


def format_path(path):
    if not path:
        return "Path is empty."

    current_start = path[0][0]
    current_start_time = path[0][1]
    current_line = path[0][2]

    formatted_path = []

    for i, (stop_name, time, line) in enumerate(path[1:], start=1):
        if line != current_line or i == len(path) - 1:
            if line == current_line:
                stop_name = path[-1][0]
                time = path[-1][1]
            formatted_path.append(
                f"{current_start} ({minutes_to_time(current_start_time)}) -> "
                f"{stop_name} on {current_line} ({minutes_to_time(time)})"
            )
            current_start = stop_name
            current_start_time = time
            current_line = line

    return "\n".join(formatted_path)
