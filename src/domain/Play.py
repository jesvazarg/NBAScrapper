class Play:
    def __init__(self, game_id: str = "", team_id: str = "", quarter: int = 1, play_time: str = "12:00", text: str = "",
                 id: str = ""):
        self.id = str(id)
        self.game_id = str(game_id) if game_id is not None else None
        self.team_id = str(team_id) if team_id is not None else None
        self.quarter = int(quarter)
        self.play_time = str(play_time)
        self.text = str(text)

    def __str__(self):
        return "id: " + self.id + ", game_id: " + self.game_id + ", team_id: " + self.team_id \
            + ", quarter: " + str(self.quarter) + ", play_time: " + str(self.play_time)
