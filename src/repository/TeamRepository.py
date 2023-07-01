from NBAScrapper.src.domain.Team import Team
from NBAScrapper.src.domain.TeamHist import TeamHist
from NBAScrapper.src.utils import DataBase
from NBAScrapper.src.utils.DataBase import Connection


def add_team(connection: Connection, team: Team):
    """Insert a new team into database from team object with zero stats"""
    insert_team = ("INSERT INTO team "
                   "(id, name, logo, conference, division, coach, arena, old_id) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    data_team = (team.id, team.name, team.logo, team.conference, team.division, team.coach, team.arena, "-")
    DataBase.execute(connection, insert_team, data_team)


def get_all_teams_id(connection: Connection) -> list[str]:
    """Get all id teams from database"""
    query = "SELECT id " \
            "FROM team " \
            "WHERE conference IS NOT null AND division IS NOT null"
    DataBase.execute(connection, query)
    return [row[0] for row in connection.cursor.fetchall()]


def get_all_teams(connection: Connection) -> list[Team]:
    """Get all teams from database"""
    query = "SELECT id, name, logo, conference, division, coach, arena, old_id, game, point, " \
            "tp, tpa, dp, dpa, ft, fta, orb, drb, ast, stl, blk, tov, foul, drw " \
            "FROM team " \
            "WHERE conference IS NOT null AND division IS NOT null"
    DataBase.execute(connection, query)
    return [Team(team[0], team[1], team[2], team[3], team[4], team[5], team[6], team[7], team[8], team[9], team[10],
                 team[11], team[12], team[13], team[14], team[15], team[16], team[17], team[18], team[19], team[20],
                 team[21], team[22], team[23])
            for team in connection.cursor.fetchall()]


def get_team(connection: Connection, team_id: str) -> Team | None:
    """Get game with id = team_id"""
    query = "SELECT id, name, logo, conference, division, coach, arena, old_id, game, point, " \
            "tp, tpa, dp, dpa, ft, fta, orb, drb, ast, stl, blk, tov, foul, drw " \
            "FROM team " \
            "WHERE id='" + str(team_id) + "'"
    DataBase.execute(connection, query)
    team = connection.cursor.fetchone()
    if team is None:
        return None
    else:
        return Team(team[0], team[1], team[2], team[3], team[4], team[5], team[6], team[7], team[8], team[9], team[10],
                    team[11], team[12], team[13], team[14], team[15], team[16], team[17], team[18], team[19], team[20],
                    team[21], team[22], team[23])


def get_team_history(connection: Connection, team_id: str, season_id: int) -> TeamHist | None:
    """Get the team history with team = team_id and season = season_id"""
    query = "SELECT id, team_id, season_id, game, point, tp, tpa, dp, dpa, ft, fta, orb, " \
            "drb, ast, stl, blk, tov, foul, drw " \
            "FROM team_hist " \
            "WHERE team_id='" + str(team_id) + "' AND season_id=" + str(season_id)
    DataBase.execute(connection, query)
    team_hist = connection.cursor.fetchone()
    if team_hist is None:
        return None
    else:
        return TeamHist(team_hist[1], team_hist[2], team_hist[3], team_hist[4], team_hist[5], team_hist[6],
                        team_hist[7], team_hist[8], team_hist[9], team_hist[10], team_hist[11], team_hist[12],
                        team_hist[13], team_hist[14], team_hist[15], team_hist[16], team_hist[17], team_hist[18])


def add_team_history(connection: Connection, team_hist: TeamHist):
    """Insert a new team history into database from team_hist object with ALL stats"""
    insert_team_hist = ("INSERT INTO team_hist "
                        "(id, team_id, season_id, game, point, tp, tpa, dp, dpa, ft, fta, "
                        "orb, drb, ast, stl, blk, tov, foul, drw) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data_team_hist = (
        team_hist.id, team_hist.team_id, team_hist.season_id, team_hist.game, team_hist.point, team_hist.tp,
        team_hist.tpa, team_hist.dp, team_hist.dpa, team_hist.ft, team_hist.fta, team_hist.orb, team_hist.drb,
        team_hist.ast, team_hist.stl, team_hist.blk, team_hist.tov, team_hist.foul, team_hist.drw)
    DataBase.execute(connection, insert_team_hist, data_team_hist)


def reset_score(connection: Connection, team_id: str):
    """Remove information from the team to not belong to the league"""
    update_team = ("UPDATE team "
                   "SET game=0, point=0, "
                   "tp=0, tpa=0, dp=0, dpa=0, ft=0, fta=0, orb=0, drb=0, ast=0, stl=0, blk=0, tov=0, foul=0, drw=0 "
                   "WHERE id='" + str(team_id) + "'")
    DataBase.execute(connection, update_team)


def update_team_score(connection: Connection, team: Team):
    """Update team score and stats from team object"""
    update_team = ("UPDATE team "
                   "SET game=%s, point=%s, tp=%s, tpa=%s, dp=%s, dpa=%s, ft=%s, fta=%s, "
                   "orb=%s, drb=%s, ast=%s, stl=%s, blk=%s, tov=%s, foul=%s, drw=%s "
                   "WHERE id=%s")
    data_team = (team.game, team.point, team.tp, team.tpa, team.dp, team.dpa, team.ft, team.fta, team.orb, team.drb,
                 team.ast, team.stl, team.blk, team.tov, team.foul, team.drw, team.id)
    DataBase.execute(connection, update_team, data_team)


def update_team_history_score(connection: Connection, team_hist: TeamHist):
    """Update team history score and stats from team_hist object"""
    update_team_hist = ("UPDATE team_hist "
                        "SET game=%s, point=%s, tp=%s, tpa=%s, dp=%s, dpa=%s, ft=%s, fta=%s, "
                        "orb=%s, drb=%s, ast=%s, stl=%s, blk=%s, tov=%s, foul=%s, drw=%s "
                        "WHERE team_id=%s AND season_id=%s")
    data_team_hist = (team_hist.game, team_hist.point, team_hist.tp, team_hist.tpa, team_hist.dp, team_hist.dpa,
                      team_hist.ft, team_hist.fta, team_hist.orb, team_hist.drb, team_hist.ast, team_hist.stl,
                      team_hist.blk, team_hist.tov, team_hist.foul, team_hist.drw, team_hist.team_id,
                      team_hist.season_id)
    DataBase.execute(connection, update_team_hist, data_team_hist)


def update_team_information(connection: Connection, team: Team):
    """Update team information from team object"""
    update_team = ("UPDATE team "
                   "SET name=%s, logo=%s, conference=%s, division=%s, coach=%s, arena=%s "
                   "WHERE id=%s")
    data_team = (team.name, team.logo, team.conference, team.division, team.coach, team.arena, team.id)
    DataBase.execute(connection, update_team, data_team)


def remove_team(connection: Connection, team_id: str):
    """Remove information from the team to not belong to the league"""
    update_team = ("UPDATE team "
                   "SET conference=null, division=null, coach=null, game=0, point=0, "
                   "tp=0, tpa=0, dp=0, dpa=0, ft=0, fta=0, orb=0, drb=0, ast=0, stl=0, blk=0, tov=0, foul=0, drw=0 "
                   "WHERE id='" + str(team_id) + "'")
    DataBase.execute(connection, update_team)


def get_number_teams_season(connection: Connection, season_id: int) -> int:
    """Get number of team history in a specific season"""
    query = ("SELECT count(*) "
             "FROM team_hist "
             "WHERE season_id=" + str(season_id))
    DataBase.execute(connection, query)
    return int(connection.cursor.fetchone()[0])


def get_number_teams_current_season(connection: Connection) -> int:
    """Get number of team history in a specific season"""
    query = ("SELECT count(*) "
             "FROM team "
             "WHERE conference IS NOT null AND division IS NOT null")
    DataBase.execute(connection, query)
    return int(connection.cursor.fetchone()[0])


def add_old_id(connection: Connection, team: Team, new_id: str):
    """Insert a new old_id in the team into database"""

    new_old_id = team.old_id + str(new_id)

    update_team = ("UPDATE team "
                   "SET old_id='" + new_old_id + "-' "
                   "WHERE id='" + team.id + "'")
    DataBase.execute(connection, update_team)


def get_teams_by_old_id(connection: Connection, old_id: str) -> list[Team]:
    """Get all teams with the same old_id from database"""
    query = "SELECT id, name, logo, conference, division, coach, arena, old_id, game, point, " \
            "tp, tpa, dp, dpa, ft, fta, orb, drb, ast, stl, blk, tov, foul, drw " \
            "FROM team " \
            "WHERE old_id LIKE '%-" + str(old_id) + "-%'"
    DataBase.execute(connection, query)
    return [Team(team[0], team[1], team[2], team[3], team[4], team[5], team[6], team[7], team[8], team[9], team[10],
                 team[11], team[12], team[13], team[14], team[15], team[16], team[17], team[18], team[19], team[20],
                 team[21], team[22], team[23])
            for team in connection.cursor.fetchall()]


def delete_teams_from_season(connection: Connection, season_id: int):
    """Remove all team_hist from the season"""
    delete_team_hist = ("DELETE FROM team_hist "
                        "WHERE season_id=" + str(season_id))
    DataBase.execute(connection, delete_team_hist)
