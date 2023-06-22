class SeasonMonth:
    def __init__(self, month: str, season_id: int, id: int = -1):
        self.id = int(id)
        self.month = str(month)
        self.season_id = int(season_id) if season_id is not None else None

    def __str__(self):
        return "SeasonMonth -> id: " + str(self.id) + ", month: " + self.month + ", season_id: " + str(self.season_id)
