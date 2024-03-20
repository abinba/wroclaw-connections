def time_to_minutes(time_str: str):
    h, m, s = map(int, time_str.split(":"))
    return h * 60 + m + s / 60.0


def minutes_to_time(minutes: float):
    h = int(minutes // 60)
    m = int(minutes % 60)
    s = int((minutes - int(minutes)) * 60)
    return f"{h}:{m}:{s}"
