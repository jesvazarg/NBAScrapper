from NBAScrapper.src.domain.FoulPlay import FoulPlay
from NBAScrapper.src.domain.FreeThrowPlay import FreeThrowPlay
from NBAScrapper.src.domain.ReboundPlay import ReboundPlay
from NBAScrapper.src.domain.SubstitutionPlay import SubstitutionPlay
from NBAScrapper.src.domain.ThreePointerPlay import ThreePointerPlay
from NBAScrapper.src.domain.TurnoverPlay import TurnoverPlay
from NBAScrapper.src.domain.TwoPointerPlay import TwoPointerPlay
from NBAScrapper.src.utils import DataBase
from NBAScrapper.src.utils.DataBase import Connection


def create_play_id(connection: Connection, table: str, game_id: str) -> int:
    """Create an id to play in a specific game"""
    query = ("SELECT count(*) "
             "FROM " + str(table) + " "
             "WHERE game_id='" + str(game_id) + "'")
    DataBase.execute(connection, query)
    return int(connection.cursor.fetchone()[0])


def add_tree_points(connection: Connection, tree_points: ThreePointerPlay, count: int):
    """Create an id and insert a new three_pointer play into database from ThreePointerPlay"""
    play_id = tree_points.game_id + str(count).zfill(3)

    insert_tree_points = ("INSERT INTO three_pointer_play "
                          "(id, game_id, team_id, quarter, play_time, text, distance, hit, player_id, assist_id, block_id) "
                          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data_tree_points = (play_id, tree_points.game_id, tree_points.team_id, tree_points.quarter, tree_points.play_time,
                        tree_points.text, tree_points.distance, tree_points.hit, tree_points.player_id,
                        tree_points.assist_id, tree_points.block_id)
    DataBase.execute(connection, insert_tree_points, data_tree_points)


def add_two_points(connection: Connection, two_points: TwoPointerPlay, count: int):
    """Create an id and insert a new two_pointer play into database from TwoPointerPlay"""
    play_id = two_points.game_id + str(count).zfill(3)

    insert_two_points = ("INSERT INTO two_pointer_play "
                         "(id, game_id, team_id, quarter, play_time, text, distance, hit, player_id, assist_id, block_id) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data_two_points = (play_id, two_points.game_id, two_points.team_id, two_points.quarter, two_points.play_time,
                       two_points.text, two_points.distance, two_points.hit, two_points.player_id, two_points.assist_id,
                       two_points.block_id)
    DataBase.execute(connection, insert_two_points, data_two_points)


def add_free_throw(connection: Connection, free_throw: FreeThrowPlay, count: int):
    """Create an id and insert a new free_throw play into database from FreeThrowPlay"""
    play_id = free_throw.game_id + str(count).zfill(3)

    insert_free_throw = ("INSERT INTO free_throw_play "
                         "(id, game_id, team_id, quarter, play_time, text, hit, player_id) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    data_free_throw = (play_id, free_throw.game_id, free_throw.team_id, free_throw.quarter, free_throw.play_time,
                       free_throw.text, free_throw.hit, free_throw.player_id)
    DataBase.execute(connection, insert_free_throw, data_free_throw)


def add_rebound(connection: Connection, rebound: ReboundPlay, count: int):
    """Create an id and insert a new rebound play into database from ReboundPlay"""
    play_id = rebound.game_id + str(count).zfill(3)

    insert_rebound = ("INSERT INTO rebound_play "
                      "(id, game_id, team_id, quarter, play_time, text, type, player_id) "
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    data_rebound = (play_id, rebound.game_id, rebound.team_id, rebound.quarter, rebound.play_time, rebound.text,
                    rebound.type, rebound.player_id)
    DataBase.execute(connection, insert_rebound, data_rebound)


def add_turnover(connection: Connection, turnover: TurnoverPlay, count: int):
    """Create an id and insert a new turnover play into database from TurnoverPlay"""
    play_id = turnover.game_id + str(count).zfill(3)

    insert_turnover = ("INSERT INTO turnover_play "
                       "(id, game_id, team_id, quarter, play_time, text, type, player_id, steal_id) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data_turnover = (play_id, turnover.game_id, turnover.team_id, turnover.quarter, turnover.play_time, turnover.text,
                     turnover.type, turnover.player_id, turnover.steal_id)
    DataBase.execute(connection, insert_turnover, data_turnover)


def add_foul(connection: Connection, foul: FoulPlay, count: int):
    """Create an id and insert a new foul play into database from FoulPlay"""
    play_id = foul.game_id + str(count).zfill(3)

    insert_foul = ("INSERT INTO foul_play "
                   "(id, game_id, team_id, quarter, play_time, text, type, player_id, drawn_id) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data_foul = (play_id, foul.game_id, foul.team_id, foul.quarter, foul.play_time, foul.text, foul.type, foul.player_id,
                 foul.drawn_id)
    DataBase.execute(connection, insert_foul, data_foul)


def add_substitution(connection: Connection, substitution: SubstitutionPlay, count: int):
    """Create an id and insert a new substitution play into database from SubstitutionPlay"""
    play_id = substitution.game_id + str(count).zfill(3)

    insert_substitution = ("INSERT INTO substitution_play "
                           "(id, game_id, team_id, quarter, play_time, text,  enter_id, leave_id) "
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    data_substitution = (play_id, substitution.game_id, substitution.team_id, substitution.quarter, substitution.play_time,
                         substitution.text, substitution.enter_id, substitution.leave_id)
    DataBase.execute(connection, insert_substitution, data_substitution)


def get_three_pointer_play(connection: Connection, three_pointer_id: str) -> ThreePointerPlay | None:
    """Get the three pointer play with id = three_pointer_id"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, distance, hit, player_id, assist_id, block_id " \
            "FROM three_pointer_play " \
            "WHERE id='" + str(three_pointer_id) + "'"
    DataBase.execute(connection, query)
    three_pointer = connection.cursor.fetchone()
    if three_pointer is None:
        return None
    else:
        return ThreePointerPlay(three_pointer[0], three_pointer[1], three_pointer[2], three_pointer[3],
                                three_pointer[4], three_pointer[5], three_pointer[6], three_pointer[7],
                                three_pointer[8], three_pointer[9], three_pointer[10])


def get_three_pointers_by_game(connection: Connection, game_id: str) -> list[ThreePointerPlay]:
    """Get ALL ThreePointerPlay saved in a specific game"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, distance, hit, player_id, assist_id, block_id " \
            "FROM three_pointer_play " \
            "WHERE game_id='" + str(game_id) + "'"
    DataBase.execute(connection, query)
    three_pointers = connection.cursor.fetchall()
    return [ThreePointerPlay(three_pointer[0], three_pointer[1], three_pointer[2], three_pointer[3], three_pointer[4],
                             three_pointer[5], three_pointer[6], three_pointer[7], three_pointer[8],
                             three_pointer[9], three_pointer[10]) for three_pointer in three_pointers]


def get_two_pointer_play(connection: Connection, two_pointer_id: str) -> TwoPointerPlay | None:
    """Get the two pointer play with id = two_pointer_id"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, distance, hit, player_id, assist_id, block_id " \
            "FROM two_pointer_play " \
            "WHERE id='" + str(two_pointer_id) + "'"
    DataBase.execute(connection, query)
    two_pointer = connection.cursor.fetchone()
    if two_pointer is None:
        return None
    else:
        return TwoPointerPlay(two_pointer[0], two_pointer[1], two_pointer[2], two_pointer[3], two_pointer[4],
                              two_pointer[5], two_pointer[6], two_pointer[7], two_pointer[8], two_pointer[9],
                              two_pointer[10])


def get_two_pointers_by_game(connection: Connection, game_id: str) -> list[TwoPointerPlay]:
    """Get ALL TwoPointerPlay saved in a specific game"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, distance, hit, player_id, assist_id, block_id " \
            "FROM two_pointer_play " \
            "WHERE game_id='" + str(game_id) + "'"
    DataBase.execute(connection, query)
    two_pointers = connection.cursor.fetchall()
    return [TwoPointerPlay(two_pointer[0], two_pointer[1], two_pointer[2], two_pointer[3], two_pointer[4],
                           two_pointer[5], two_pointer[6], two_pointer[7], two_pointer[8], two_pointer[9],
                           two_pointer[10]) for two_pointer in two_pointers]


def get_free_throw_play(connection: Connection, free_throw_id: str) -> FreeThrowPlay | None:
    """Get the free throw play with id = free_throw_id"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, hit, player_id " \
            "FROM free_throw_play " \
            "WHERE id='" + str(free_throw_id) + "'"
    DataBase.execute(connection, query)
    free_throw = connection.cursor.fetchone()
    if free_throw is None:
        return None
    else:
        return FreeThrowPlay(free_throw[0], free_throw[1], free_throw[2], free_throw[3], free_throw[4], free_throw[5],
                             free_throw[6], free_throw[7])


def get_free_throws_by_game(connection: Connection, game_id: str) -> list[FreeThrowPlay]:
    """Get ALL FreeThrowPlay saved in a specific game"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, hit, player_id " \
            "FROM free_throw_play " \
            "WHERE game_id='" + str(game_id) + "'"
    DataBase.execute(connection, query)
    free_throws = connection.cursor.fetchall()
    return [FreeThrowPlay(free_throw[0], free_throw[1], free_throw[2], free_throw[3], free_throw[4], free_throw[5],
                          free_throw[6], free_throw[7]) for free_throw in free_throws]


def get_rebound_play(connection: Connection, rebound_id: str) -> ReboundPlay | None:
    """Get the rebound play with id = rebound_id"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, type, player_id " \
            "FROM rebound_play " \
            "WHERE id='" + str(rebound_id) + "'"
    DataBase.execute(connection, query)
    rebound = connection.cursor.fetchone()
    if rebound is None:
        return None
    else:
        return ReboundPlay(rebound[0], rebound[1], rebound[2], rebound[3], rebound[4], rebound[5], rebound[6],
                           rebound[7])


def get_rebounds_by_game(connection: Connection, game_id: str) -> list[ReboundPlay]:
    """Get ALL ReboundPlay saved in a specific game"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, type, player_id " \
            "FROM rebound_play " \
            "WHERE game_id='" + str(game_id) + "'"
    DataBase.execute(connection, query)
    rebounds = connection.cursor.fetchall()
    return [ReboundPlay(rebound[0], rebound[1], rebound[2], rebound[3], rebound[4], rebound[5], rebound[6],
                        rebound[7]) for rebound in rebounds]


def get_turnover_play(connection: Connection, turnover_id: str) -> TurnoverPlay | None:
    """Get the turnover play with id = turnover_id"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, type, player_id, steal_id " \
            "FROM turnover_play " \
            "WHERE id='" + str(turnover_id) + "'"
    DataBase.execute(connection, query)
    turnover = connection.cursor.fetchone()
    if turnover is None:
        return None
    else:
        return TurnoverPlay(turnover[0], turnover[1], turnover[2], turnover[3], turnover[4], turnover[5], turnover[6],
                            turnover[7], turnover[8])


def get_turnovers_by_game(connection: Connection, game_id: str) -> list[TurnoverPlay]:
    """Get ALL TurnoverPlay saved in a specific game"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, type, player_id, steal_id " \
            "FROM turnover_play " \
            "WHERE game_id='" + str(game_id) + "'"
    DataBase.execute(connection, query)
    turnovers = connection.cursor.fetchall()
    return [TurnoverPlay(turnover[0], turnover[1], turnover[2], turnover[3], turnover[4], turnover[5], turnover[6],
                         turnover[7], turnover[8]) for turnover in turnovers]


def get_foul_play(connection: Connection, foul_id: str) -> FoulPlay | None:
    """Get the foul play with id = foul_id"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, type, player_id, drawn_id " \
            "FROM foul_play " \
            "WHERE id='" + str(foul_id) + "'"
    DataBase.execute(connection, query)
    foul = connection.cursor.fetchone()
    if foul is None:
        return None
    else:
        return FoulPlay(foul[0], foul[1], foul[2], foul[3], foul[4], foul[5], foul[6], foul[7], foul[8])


def get_fouls_by_game(connection: Connection, game_id: str) -> list[FoulPlay]:
    """Get ALL FoulPlay saved in a specific game"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, type, player_id, drawn_id " \
            "FROM foul_play " \
            "WHERE game_id='" + str(game_id) + "'"
    DataBase.execute(connection, query)
    fouls = connection.cursor.fetchall()
    return [FoulPlay(foul[0], foul[1], foul[2], foul[3], foul[4], foul[5], foul[6], foul[7], foul[8]) for foul in fouls]


def get_substitution_play(connection: Connection, substitution_id: str) -> SubstitutionPlay | None:
    """Get the substitution play with id = substitution_id"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, enter_id, leave_id " \
            "FROM substitution_play " \
            "WHERE id='" + str(substitution_id) + "'"
    DataBase.execute(connection, query)
    substitution = connection.cursor.fetchone()
    if substitution is None:
        return None
    else:
        return SubstitutionPlay(substitution[0], substitution[1], substitution[2], substitution[3], substitution[4],
                                substitution[5], substitution[6], substitution[7])


def get_substitutions_by_game(connection: Connection, game_id: str) -> list[SubstitutionPlay]:
    """Get ALL SubstitutionPlay saved in a specific game"""
    query = "SELECT game_id, team_id, quarter, play_time, text, id, player_id, drawn_id " \
            "FROM foul_play " \
            "WHERE game_id='" + str(game_id) + "'"
    DataBase.execute(connection, query)
    substitutions = connection.cursor.fetchall()
    return [SubstitutionPlay(substitution[0], substitution[1], substitution[2], substitution[3], substitution[4],
                             substitution[5], substitution[6], substitution[7]) for substitution in substitutions]


def delete_tree_points_from_season(connection: Connection, season_id: int):
    """Remove all three_pointer from the season"""
    delete_tree_points = ("DELETE FROM three_pointer_play "
                          "WHERE game_id IN "
                          "(SELECT id FROM game WHERE season_month_id IN "
                          "(SELECT id FROM season_month WHERE season_id=" + str(season_id) + "))")
    DataBase.execute(connection, delete_tree_points)


def delete_two_points_from_season(connection: Connection, season_id: int):
    """Remove all two_pointer from the season"""
    delete_two_points = ("DELETE FROM two_pointer_play "
                         "WHERE game_id IN "
                         "(SELECT id FROM season_month WHERE season_id=" + str(season_id) + "))")
    DataBase.execute(connection, delete_two_points)


def delete_free_throw_from_season(connection: Connection, season_id: int):
    """Remove all free_throw from the season"""
    delete_free_throw = ("DELETE FROM free_throw_play "
                         "WHERE game_id IN "
                         "(SELECT id FROM game WHERE season_month_id IN "
                         "(SELECT id FROM season_month WHERE season_id=" + str(season_id) + "))")
    DataBase.execute(connection, delete_free_throw)


def delete_rebound_from_season(connection: Connection, season_id: int):
    """Remove all rebound from the season"""
    delete_rebound = ("DELETE FROM rebound_play "
                      "WHERE game_id IN "
                      "(SELECT id FROM game WHERE season_month_id IN "
                      "(SELECT id FROM season_month WHERE season_id=" + str(season_id) + "))")
    DataBase.execute(connection, delete_rebound)


def delete_foul_from_season(connection: Connection, season_id: int):
    """Remove all foul from the season"""
    delete_foul = ("DELETE FROM foul_play "
                   "WHERE game_id IN "
                   "(SELECT id FROM season_month WHERE season_id=" + str(season_id) + "))")
    DataBase.execute(connection, delete_foul)


def delete_turnover_from_season(connection: Connection, season_id: int):
    """Remove all turnover from the season"""
    delete_turnover = ("DELETE FROM turnover_play "
                       "WHERE game_id IN "
                       "(SELECT id FROM game WHERE season_month_id IN "
                       "(SELECT id FROM season_month WHERE season_id=" + str(season_id) + "))")
    DataBase.execute(connection, delete_turnover)


def delete_substitution_from_season(connection: Connection, season_id: int):
    """Remove all substitution from the season"""
    delete_substitution = ("DELETE FROM substitution_play "
                           "WHERE game_id IN "
                           "(SELECT id FROM game WHERE season_month_id IN "
                           "(SELECT id FROM season_month WHERE season_id=" + str(season_id) + "))")
    DataBase.execute(connection, delete_substitution)
