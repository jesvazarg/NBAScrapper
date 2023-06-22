from datetime import datetime, timedelta


class Game:
    def __init__(self, id: str, season_month_id: int, type: str, game_date: datetime | str, game_time: timedelta | str,
                 visitor_team_id: str, home_team_id: str, visitor_point: int = 0, home_point: int = 0):
        self.id = id
        self.season_month_id = int(season_month_id)
        self.type = str(type)
        self.game_date = game_date
        self.game_time = game_time
        self.visitor_team_id = str(visitor_team_id) if visitor_team_id is not None else None
        self.home_team_id = str(home_team_id) if home_team_id is not None else None
        self.visitor_point = int(visitor_point)
        self.home_point = int(home_point)

    def __str__(self):
        return "Game -> id: " + self.id + ", season_month_id: " + str(self.season_month_id) + \
            ", type: " + self.type + ", game_date: " + str(self.game_date) + ", game_time: " + str(self.game_time) + \
            ", visitor_team_id: " + self.visitor_team_id + ", home_team_id: " + self.home_team_id + \
            ", visitor_point: " + str(self.visitor_point) + ", home_point: " + str(self.home_point)

    def make_visitor_point(self, point: int):
        """Add the point to the visitor points"""
        self.visitor_point += point

    def make_home_point(self, point: int):
        """Add the point to the home points"""
        self.home_point += point
