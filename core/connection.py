class Connection:
    def __init__(
        self,
        line: str,
        company: str,
        departure_time_minutes: float,
        arrival_time_minutes: float,
        travel_time_minutes: float,
    ):
        self.line = line
        self.company = company
        self.departure_time_minutes = departure_time_minutes
        self.arrival_time_minutes = arrival_time_minutes
        self.travel_time_minutes = travel_time_minutes

    @property
    def line_company(self):
        return f"{self.line} ({self.company})"

    def __str__(self):
        return f"{self.line_company} ({self.departure_time_minutes} -> {self.arrival_time_minutes})"
