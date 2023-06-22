from NBAScrapper.src.domain.Player import Player


class PlayerHist:
    def __init__(self, player_id: str, team_id: str, season_id: int, game: int = 0, point: int = 0,
                 mp: int = 0, tp: int = 0, tpa: int = 0, dp: int = 0, dpa: int = 0,
                 ft: int = 0, fta: int = 0, orb: int = 0, drb: int = 0, ast: int = 0, stl: int = 0, blk: int = 0,
                 tov: int = 0, foul: int = 0, drw: int = 0):
        self.id = self.get_player_hist_id(player_id, team_id, season_id)
        self.player_id = str(player_id) if player_id is not None else None
        self.team_id = str(team_id) if team_id is not None else None
        self.season_id = int(season_id) if season_id is not None else None
        self.game = int(game)
        self.point = int(point)
        self.mp = int(mp)
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
        return "PlayerHist -> id: " + self.id + ", player_id: " + self.player_id + ", team_id: " + self.team_id + \
            ", season_id: " + str(self.season_id) + ", game: " + str(self.game) + ", point: " + str(self.point) + \
            ", mp: " + str(self.mp // 3600) + ":" + str(self.mp // 60 - (self.mp // 3600)*60) + ":" + str(self.mp % 60)\
            + ", STATS[TP: " + str(self.tp) + ", TPA: " + str(self.tpa) + \
            ", DP: " + str(self.dp) + ", DPA: " + str(self.dpa) + ", FT: " + str(self.ft) + ", FTA: " + str(self.fta) +\
            ", ORB: " + str(self.orb) + ", DRB: " + str(self.drb) + ", AST: " + str(self.ast) + \
            ", STL: " + str(self.stl) + ", BLK: " + str(self.blk) + ", TOV: " + str(self.tov) + \
            ", FOUL: " + str(self.foul) + ", DRW: " + str(self.drw) + "]"

    def add_player_stats(self, player: Player):
        self.game = player.game
        self.point = player.point
        self.mp = player.mp
        self.tp = player.tp
        self.tpa = player.tpa
        self.dp = player.dp
        self.dpa = player.dpa
        self.ft = player.ft
        self.fta = player.fta
        self.orb = player.orb
        self.drb = player.drb
        self.ast = player.ast
        self.stl = player.stl
        self.blk = player.blk
        self.tov = player.tov
        self.foul = player.foul
        self.drw = player.drw

    def play_game(self):
        """Increase game by 1"""
        self.game += 1

    def add_minutes_played(self, time: str):
        # self.mp += timedelta(minutes=int(time.split(":")[0]), seconds=int(time.split(":")[1]))
        self.mp += int(time.split(":")[0]) * 60 + int(time.split(":")[1])

    def start_game(self):
        # self.mp += timedelta(minutes=48)
        self.mp += 4 * 12 * 60

    def enter_game(self, time: str, quarter: int):
        # self.mp += (timedelta(minutes=int(time.split(":")[1]), seconds=int(time.split(":")[2])) +
                    # (4 - quarter) * timedelta(minutes=12))
        self.mp += int(time.split(":")[0]) * 60 + int(time.split(":")[1]) + (4 - quarter) * 12 * 60

    def leave_game(self, time: str, quarter: int):
        # self.mp -= (timedelta(minutes=int(time.split(":")[1]), seconds=int(time.split(":")[2])) +
                    # (4 - quarter) * timedelta(minutes=12))
        self.mp -= int(time.split(":")[0]) * 60 + int(time.split(":")[1]) + (4 - quarter) * 12 * 60

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
        """Increase foul by 1"""
        self.foul += 1

    def make_drawn(self):
        """Increase drw by 1"""
        self.drw += 1

    @classmethod
    def get_player_hist_id(cls, player_id: str, team_id: str, season_id: int) -> str:
        """Create id from a player_hist"""
        return player_id + str(season_id) + team_id
