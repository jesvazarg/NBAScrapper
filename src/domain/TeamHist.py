from NBAScrapper.src.domain.Team import Team


class TeamHist:
    def __init__(self, team_id: str, season_id: int, game: int = 0, point: int = 0, tp: int = 0, tpa: int = 0,
                 dp: int = 0, dpa: int = 0, ft: int = 0, fta: int = 0, orb: int = 0, drb: int = 0, ast: int = 0,
                 stl: int = 0, blk: int = 0, tov: int = 0, foul: int = 0, drw: int = 0):
        self.id = team_id + str(season_id)
        self.team_id = str(team_id) if team_id is not None else None
        self.season_id = int(season_id) if season_id is not None else None
        self.game = int(game)
        self.point = int(point)
        self.tp = int(tp)
        self.tpa = int(tpa)
        self.dp = int(dp)
        self.dpa = int(dpa)
        self.ft = int(ft)
        self.fta = int(fta)
        self.orb = int(orb)
        self.drb = int(drb)
        self.ast = int(ast)
        self.stl = int(stl)
        self.blk = int(blk)
        self.tov = int(tov)
        self.foul = int(foul)
        self.drw = int(drw)

    def __str__(self):
        return "TeamHist -> id: " + self.id + ", team_id: " + self.team_id + ", season_id: " + str(self.season_id) + \
            ", game: " + str(self.game) + ", point: " + str(self.point) + ", STATS[TP: " + str(self.tp) + \
            ", TPA: " + str(self.tpa) + ", DP: " + str(self.dp) + ", DPA: " + str(self.dpa) + \
            ", FT: " + str(self.ft) + ", FTA: " + str(self.fta) + ", ORB: " + str(self.orb) + \
            ", DRB: " + str(self.drb) + ", AST: " + str(self.ast) + ", STL: " + str(self.stl) + \
            ", BLK: " + str(self.blk) + ", TOV: " + str(self.tov) + ", FOUL: " + str(self.foul) + \
            ", DRW: " + str(self.drw) + "]"

    def add_team_stats(self, team: Team):
        self.game = team.game
        self.point = team.point
        self.tp = team.tp
        self.tpa = team.tpa
        self.dp = team.dp
        self.dpa = team.dpa
        self.ft = team.ft
        self.fta = team.fta
        self.orb = team.orb
        self.drb = team.drb
        self.ast = team.ast
        self.stl = team.stl
        self.blk = team.blk
        self.tov = team.tov
        self.foul = team.foul
        self.drw = team.drw


    def play_game(self):
        """Increase game by 1"""
        self.game += 1

    def make_three_point(self):
        """Increase tp by 1, tpa by 1 and point by 3"""
        self.tp += 1
        self.tpa += 1
        self.point += 3

    def fail_three_point(self):
        """Increase tpa by 1"""
        self.tpa += 1

    def make_two_point(self):
        """Increase dp by 1, dpa by 1 and point by 2"""
        self.dp += 1
        self.dpa += 1
        self.point += 2

    def fail_two_point(self):
        """Increase dpa by 1"""
        self.dpa += 1

    def make_free_throw(self):
        """Increase ft by 1, fta by 1 and point by 1"""
        self.ft += 1
        self.fta += 1
        self.point += 1

    def fail_free_throw(self):
        """Increase fta by 1"""
        self.fta += 1

    def make_offensive_rebound(self):
        """Increase orb by 1"""
        self.orb += 1

    def make_defensive_rebound(self):
        """Increase drb by 1"""
        self.drb += 1

    def make_assist(self):
        """Increase ast by 1"""
        self.ast += 1

    def make_steal(self):
        """Increase stl by 1"""
        self.stl += 1

    def make_block(self):
        """Increase blk by 1"""
        self.blk += 1

    def make_turnover(self):
        """Increase tov by 1"""
        self.tov += 1

    def make_foul(self):
        """Reduce foul by 1"""
        self.foul += 1

    def remove_foul(self):
        """Increase foul by 1"""
        self.foul -= 1

    def make_drawn(self):
        """Increase drw by 1"""
        self.drw += 1
