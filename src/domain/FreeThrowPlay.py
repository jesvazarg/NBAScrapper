from NBAScrapper.src.domain.Play import Play


class FreeThrowPlay(Play):
    def __init__(self, game_id: str = "", team_id: str = "", quarter: int = 1, play_time: str = "12:00", text: str = "",
                 id: str = "", hit: bool = False, player_id: str = ""):
        super().__init__(game_id, team_id, quarter, play_time, text, id)
        self.hit = bool(hit)
        self.player_id = str(player_id) if player_id is not None else None

    def __str__(self):
        return "FreeThrowPlay -> " + super().__str__() + ", hit: " + str(self.hit)\
            + ", player_id: " + str(self.player_id)

    def init_with_play(self, play: Play, hit: bool = False, player_id: str = ""):
        super().__init__(play.game_id, play.team_id, play.quarter, play.play_time, play.text)
        self.hit = bool(hit)
        self.player_id = str(player_id) if player_id is not None else None

        return self

    def is_valid(self):
        return self.game_id is not None and self.team_id is not None and self.quarter is not None and \
            self.play_time is not None and self.text is not None and self.hit is not None and self.player_id is not None
