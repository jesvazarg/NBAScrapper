from NBAScrapper.src.domain.Play import Play


class SubstitutionPlay(Play):
    def __init__(self, game_id: str = "", team_id: str = "", quarter: int = 1, play_time: str = "12:00", text: str = "",
                 id: str = "", enter_id: str = "", leave_id: str = ""):
        super().__init__(game_id, team_id, quarter, play_time, text, id)
        self.enter_id = str(enter_id) if enter_id is not None else None
        self.leave_id = str(leave_id) if leave_id is not None else None

    def __str__(self):
        return "TurnoverPlay -> " + super().__str__() + ", enter_id: " + str(self.enter_id) + \
            ", leave_id: " + str(self.leave_id)

    def init_with_play(self, play: Play, enter_id: str = "", leave_id: str = ""):
        super().__init__(play.game_id, play.team_id, play.quarter, play.play_time, play.text)
        self.enter_id = str(enter_id) if enter_id is not None else None
        self.leave_id = str(leave_id) if leave_id is not None else None

        return self

    def is_valid(self):
        return self.game_id is not None and self.team_id is not None and self.quarter is not None and \
            self.play_time is not None and self.text is not None and self.enter_id is not None and self.leave_id is not None
