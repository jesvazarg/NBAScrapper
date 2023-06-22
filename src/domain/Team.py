class Team:
    def __init__(self, id: str, name: str, logo: str, conference: str, division: str, coach: str, arena: str,
                 old_id: str = '', game: int = 0, point: int = 0, tp: int = 0, tpa: int = 0, dp: int = 0, dpa: int = 0,
                 ft: int = 0, fta: int = 0, orb: int = 0, drb: int = 0, ast: int = 0, stl: int = 0, blk: int = 0,
                 tov: int = 0, foul: int = 0, drw: int = 0):
        self.id = str(id)
        self.name = str(name)
        self.logo = str(logo)
        self.conference = str(conference)
        self.division = str(division)
        self.coach = str(coach)
        self.arena = str(arena)
        self.old_id = str(old_id)
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

        if self.conference == "Eastern":
            self.conference = "E"
        elif self.conference == "Western":
            self.conference = "W"

        if self.division == "Atlantic":
            self.division = "AT"
        elif self.division == "Central":
            self.division = "CE"
        elif self.division == "Southeast":
            self.division = "SE"
        elif self.division == "Northwest":
            self.division = "NW"
        elif self.division == "Pacific":
            self.division = "PA"
        elif self.division == "Southwest":
            self.division = "SW"

    def __eq__(self, obj):
        return isinstance(obj, Team) and obj.id == self.id and obj.name == self.name and obj.logo == self.logo and \
            obj.conference == self.conference and obj.division == self.division and obj.coach == self.coach and \
            obj.arena == self.arena

    def __str__(self):
        return "Team -> id: " + str(self.id) + ", name: " + self.name + ", logo: " + str(self.logo) + \
            ", conference: " + str(self.conference) + ", division: " + str(self.division) + \
            ", coach: " + str(self.coach) + ", arena: " + str(self.arena) + ", old_id: " + str(self.old_id) +\
            ", game: " + str(self.game) + ", point: " + str(self.point) + ", STATS[TP: " + str(self.tp) + \
            ", TPA: " + str(self.tpa) + ", DP: " + str(self.dp) + ", DPA: " + str(self.dpa) + ", FT: " + str(self.ft) +\
            ", FTA: " + str(self.fta) + ", ORB: " + str(self.orb) + ", DRB: " + str(self.drb) + \
            ", AST: " + str(self.ast) + ", STL: " + str(self.stl) + ", BLK: " + str(self.blk) + \
            ", TOV: " + str(self.tov) + ", FOUL: " + str(self.foul) + ", DRW: " + str(self.drw) + "]"

    def is_same_id(self, id: str):
        return id in self.old_id.split("-")

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
        """Increase foul by 1"""
        self.foul += 1

    def remove_foul(self):
        """Reduce foul by 1"""
        self.foul -= 1

    def make_drawn(self):
        """Increase drw by 1"""
        self.drw += 1
