from datetime import date


class Player:
    def __init__(self, id: str, name: str, number: int, photo: str, dob: date, position: str, shoot: str,
                 height: int, weight: int, team_id: str = "", game: int = 0, point: int = 0,
                 mp: int = 0, tp: int = 0, tpa: int = 0, dp: int = 0, dpa: int = 0,
                 ft: int = 0, fta: int = 0, orb: int = 0, drb: int = 0, ast: int = 0, stl: int = 0, blk: int = 0,
                 tov: int = 0, foul: int = 0, drw: int = 0):
        self.id = str(id)
        self.name = str(name)
        try:
            self.number = int(number)
        except:
            self.number = None
            pass
        self.photo = str(photo)
        self.dob = dob
        self.position = str(position)
        self.shoot = str(shoot)
        self.height = int(height)
        self.weight = int(weight)
        self.team_id = str(team_id) if team_id is not None else None
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

        if self.shoot == "Right":
            self.shoot = "R"
        elif self.shoot == "Left":
            self.shoot = "L"

    def __eq__(self, obj):
        return isinstance(obj, Player) and obj.id == self.id and obj.name == self.name and \
            obj.photo == self.photo and obj.dob == self.dob and obj.position == self.position and \
            obj.shoot == self.shoot and obj.height == self.height and obj.weight == self.weight

    def __str__(self):
        res = "Player -> id: " + self.id + ", name: " + str(self.name) + ", number: " + str(self.number) + \
              ", photo: " + str(self.photo) + ", dob: " + str(self.dob) + ", position: " + str(self.position) + \
              ", shoot: " + str(self.shoot) + ", height: " + str(self.height) + ", weight: " + str(self.weight)
        if self.team_id != "":
            res += ", team_id: " + str(self.team_id)
        res += ", game: " + str(self.game) + ", point: " + str(self.point) + ", mp: " + str(self.mp // 3600) + ":" + \
               str(self.mp // 60 - (self.mp // 3600) * 60) + ":" + str(self.mp % 60) + \
               ", STATS[TP: " + str(self.tp) + ", TPA: " + str(self.tpa) + ", DP: " + str(self.dp) + \
               ", DPA: " + str(self.dpa) + ", FT: " + str(self.ft) + ", FTA: " + str(self.fta) + \
               ", ORB: " + str(self.orb) + ", DRB: " + str(self.drb) + ", AST: " + str(self.ast) + \
               ", STL: " + str(self.stl) + ", BLK: " + str(self.blk) + ", TOV: " + str(self.tov) + \
               ", FOUL: " + str(self.foul) + ", DRW: " + str(self.drw) + "]"

        return res

    def play_game(self):
        """Increase game by 1"""
        self.game += 1

    def add_minutes_played(self, time: str):
        # self.mp += timedelta(minutes=int(time.split(":")[0]), seconds=int(time.split(":")[1]))
        self.mp += int(time.split(":")[0])*60 + int(time.split(":")[1])

    def start_game(self):
        # self.mp += timedelta(minutes=48)
        self.mp += 4 * 12 * 60

    def enter_game(self, time: str, quarter: int):
        # self.mp += (timedelta(minutes=int(time.split(":")[1]), seconds=int(time.split(":")[2])) +
                    # (4 - quarter) * timedelta(minutes=12))
        self.mp += int(time.split(":")[0])*60 + int(time.split(":")[1]) + (4 - quarter) * 12 * 60

    def leave_game(self, time: str, quarter: int):
        # self.mp -= (timedelta(minutes=int(time.split(":")[1]), seconds=int(time.split(":")[2])) +
                    # (4 - quarter) * timedelta(minutes=12))
        self.mp -= int(time.split(":")[0])*60 + int(time.split(":")[1]) + (4 - quarter) * 12 * 60

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
