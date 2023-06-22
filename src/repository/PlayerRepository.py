from NBAScrapper.src.domain.Player import Player
from NBAScrapper.src.domain.PlayerHist import PlayerHist
from NBAScrapper.src.utils import DataBase

from NBAScrapper.src.utils.DataBase import Connection


def create_new_player(connection: Connection, player: Player):
    """Insert a new player into database from player object without score and stats"""
    insert_player = ("INSERT INTO player "
                     "(id, name, number, photo, dob, position, shoot, height, weight, team_id) "
                     "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data_player = (
        player.id, player.name, player.number, player.photo, player.dob, player.position, player.shoot, player.height,
        player.weight, player.team_id)
    DataBase.execute(connection, insert_player, data_player)


def get_all_players_id_from_team(connection: Connection, team_id: str) -> list[str]:
    """Get all id players of a team"""
    query = "SELECT id " \
            "FROM player " \
            "WHERE team_id='" + str(team_id) + "'"
    DataBase.execute(connection, query)
    return [row[0] for row in connection.cursor.fetchall()]


def get_all_players_from_team(connection: Connection, team_id: str) -> list[Player]:
    """Get all players of a team"""
    query = "SELECT id, name, number, photo, dob, position, shoot, height, weight, team_id, game, point, mp, " \
            "tp, tpa, dp, dpa, ft, fta, orb, drb, ast, stl, blk, tov, foul, drw " \
            "FROM player " \
            "WHERE team_id='" + str(team_id) + "'"
    DataBase.execute(connection, query)
    return [Player(player[0], player[1], player[2], player[3], player[4], player[5], player[6], player[7], player[8],
                   player[9], player[10], player[11], player[12], player[13], player[14], player[15], player[16],
                   player[17], player[18], player[19], player[20], player[21], player[22], player[23], player[24],
                   player[25], player[26])
            for player in connection.cursor.fetchall()]


def get_player(connection: Connection, player_id: str) -> Player | None:
    """Get a player with id = player_id"""
    query = "SELECT id, name, number, photo, dob, position, shoot, height, weight, team_id, game, point, mp, " \
            "tp, tpa, dp, dpa, ft, fta, orb, drb, ast, stl, blk, tov, foul, drw " \
            "FROM player " \
            "WHERE id='" + str(player_id) + "'"
    DataBase.execute(connection, query)
    player = connection.cursor.fetchone()
    if player is None:
        return None
    else:
        return Player(player[0], player[1], player[2], player[3], player[4], player[5], player[6], player[7], player[8],
                      player[9], player[10], player[11], player[12], player[13], player[14], player[15], player[16],
                      player[17], player[18], player[19], player[20], player[21], player[22], player[23], player[24],
                      player[25], player[26])


def get_player_history(connection: Connection, player_id: str, team_id: str, season_id: int) -> PlayerHist | None:
    """Get a player history with player = player_id and team = team_id and season = season_id"""
    query = "SELECT id, player_id, team_id, season_id, game, point, mp, tp, tpa, dp, dpa" \
            ", ft, fta, orb, drb, ast, stl, blk, tov, foul, drw " \
            "FROM player_hist " \
            "WHERE player_id='" + str(player_id) + "' AND team_id='" + str(team_id) + \
            "' AND season_id=" + str(season_id)
    DataBase.execute(connection, query)
    player_hist = connection.cursor.fetchone()
    if player_hist is None:
        return None
    else:
        return PlayerHist(player_hist[1], player_hist[2], player_hist[3], player_hist[4], player_hist[5],
                          player_hist[6], player_hist[7], player_hist[8], player_hist[9], player_hist[10],
                          player_hist[11], player_hist[12], player_hist[13], player_hist[14], player_hist[15],
                          player_hist[16], player_hist[17], player_hist[18], player_hist[19], player_hist[20])


def get_player_history_by_id(connection: Connection, player_hist_id: str,) -> PlayerHist | None:
    """Get a player history by id"""
    query = "SELECT id, player_id, team_id, season_id, game, point, mp, tp, tpa, dp, dpa" \
            ", ft, fta, orb, drb, ast, stl, blk, tov, foul, drw " \
            "FROM player_hist " \
            "WHERE id='" + str(player_hist_id) + "'"
    DataBase.execute(connection, query)
    player_hist = connection.cursor.fetchone()
    if player_hist is None:
        return None
    else:
        return PlayerHist(player_hist[1], player_hist[2], player_hist[3], player_hist[4], player_hist[5],
                          player_hist[6], player_hist[7], player_hist[8], player_hist[9], player_hist[10],
                          player_hist[11], player_hist[12], player_hist[13], player_hist[14], player_hist[15],
                          player_hist[16], player_hist[17], player_hist[18], player_hist[19], player_hist[20])


def add_player_history(connection: Connection, player_hist: PlayerHist):
    """Insert a new player history into database from player_history object"""
    insert_player_hist = ("INSERT INTO player_hist "
                          "(id, player_id, team_id, season_id, game, point, mp, "
                          "tp, tpa, dp, dpa, ft, fta, orb, drb, ast, stl, blk, tov, foul, drw) "
                          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data_player_hist = (
        player_hist.id, player_hist.player_id, player_hist.team_id, player_hist.season_id, player_hist.game,
        player_hist.point, player_hist.mp, player_hist.tp, player_hist.tpa, player_hist.dp, player_hist.dpa,
        player_hist.ft, player_hist.fta, player_hist.orb, player_hist.drb, player_hist.ast, player_hist.stl,
        player_hist.blk, player_hist.tov, player_hist.foul, player_hist.drw)
    DataBase.execute(connection, insert_player_hist, data_player_hist)


def update_player_score(connection: Connection, player: Player):
    """Update the player score"""
    update_player = ("UPDATE player "
                     "SET game=%s, point=%s, mp=%s, tp=%s, tpa=%s, dp=%s, dpa=%s, ft=%s, fta=%s, "
                     "orb=%s, drb=%s, ast=%s, stl=%s, blk=%s, tov=%s, foul=%s, drw=%s "
                     "WHERE id=%s")
    data_player = (player.game, player.point, player.mp, player.tp, player.tpa, player.dp, player.dpa, player.ft,
                   player.fta, player.orb, player.drb, player.ast, player.stl, player.blk, player.tov, player.foul,
                   player.drw, player.id)
    DataBase.execute(connection, update_player, data_player)


def update_player_history_score(connection: Connection, player_hist: PlayerHist):
    """Update the player history score"""
    update_player_hist = ("UPDATE player_hist "
                          "SET game=%s, point=%s, mp=%s, tp=%s, tpa=%s, dp=%s, dpa=%s, ft=%s, fta=%s, "
                          "orb=%s, drb=%s, ast=%s, stl=%s, blk=%s, tov=%s, foul=%s, drw=%s "
                          "WHERE player_id=%s AND team_id=%s AND season_id=%s")
    data_player_hist = (player_hist.game, player_hist.point, player_hist.mp, player_hist.tp, player_hist.tpa,
                        player_hist.dp, player_hist.dpa, player_hist.ft, player_hist.fta, player_hist.orb,
                        player_hist.drb, player_hist.ast, player_hist.stl, player_hist.blk, player_hist.tov,
                        player_hist.foul, player_hist.drw, player_hist.player_id, player_hist.team_id,
                        player_hist.season_id)
    DataBase.execute(connection, update_player_hist, data_player_hist)


def update_player_information(connection: Connection, player: Player):
    """Update the player information"""
    update_player = ("UPDATE player "
                     "SET name=%s, number=%s, photo=%s, dob=%s, position=%s, shoot=%s, height=%s, weight=%s "
                     "WHERE id=%s")
    data_player = (player.name, player.number, player.photo, player.dob, player.position, player.shoot, player.height,
                   player.weight, player.id)
    DataBase.execute(connection, update_player, data_player)


def reset_score(connection: Connection, player_id: str):
    """Remove the player team and set zero score and stats"""
    update_player = ("UPDATE player "
                     "SET game=0, point=0, mp=0, tp=0, tpa=0, dp=0, dpa=0, ft=0, fta=0, "
                     "orb=0, drb=0, ast=0, stl=0, blk=0, tov=0, foul=0, drw=0 "
                     "WHERE id='" + str(player_id) + "'")
    DataBase.execute(connection, update_player)


def player_change_team(connection: Connection, player: Player):
    """Change the player team and set zero score and stats"""
    update_player = ("UPDATE player "
                     "SET team_id=%s, game=0, point=0, mp=0, tp=0, tpa=0, dp=0, dpa=0, ft=0, fta=0, "
                     "orb=0, drb=0, ast=0, stl=0, blk=0, tov=0, foul=0, drw=0 "
                     "WHERE id=%s")
    data_player = (player.team_id, player.id)
    DataBase.execute(connection, update_player, data_player)


def leave_team(connection: Connection, player_id: str):
    """Remove the player team and set zero score and stats"""
    update_player = ("UPDATE player "
                     "SET team_id=null, game=0, point=0, mp=0, tp=0, tpa=0, dp=0, dpa=0, ft=0, fta=0, "
                     "orb=0, drb=0, ast=0, stl=0, blk=0, tov=0, foul=0, drw=0 "
                     "WHERE id='" + str(player_id) + "'")
    DataBase.execute(connection, update_player)
