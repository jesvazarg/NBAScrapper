from NBAScrapper.src.domain.Play import Play


class TurnoverPlay(Play):
    def __init__(self, game_id: str = "", team_id: str = "", quarter: int = 1, play_time: str = "12:00", text: str = "",
                 id: str = "", type: str = "", player_id: str = "", steal_id: str = ""):
        super().__init__(game_id, team_id, quarter, play_time, text, id)
        self.type = str(type)
        self.player_id = str(player_id) if player_id is not None else None
        self.steal_id = str(steal_id) if steal_id is not None else None

    def __str__(self):
        res = "TurnoverPlay -> " + super().__str__() + ", type: " + str(self.type)
        if self.player_id != "":
            res += ", player_id: " + self.player_id
        if self.steal_id != "":
            res += ", steal_id: " + self.steal_id

        return res

    def init_with_play(self, play: Play, type: str = "", player_id: str = "", steal_id: str = ""):
        super().__init__(play.game_id, play.team_id, play.quarter, play.play_time, play.text)
        self.type = str(type)
        self.player_id = str(player_id) if player_id is not None else None
        self.steal_id = str(steal_id) if steal_id is not None else None

        return self

    def is_valid(self):
        return self.game_id is not None and self.team_id is not None and self.quarter is not None and \
            self.play_time is not None and self.text is not None and self.type is not None
