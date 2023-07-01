from NBAScrapper.src.domain.Game import Game
from NBAScrapper.src.domain.GameHomePlayer import GameHomePlayer
from NBAScrapper.src.domain.GameVisitorPlayer import GameVisitorPlayer
from NBAScrapper.src.domain.Player import Player
from NBAScrapper.src.domain.PlayerHist import PlayerHist
from NBAScrapper.src.utils import DataBase
from NBAScrapper.src.utils.DataBase import Connection


def add_game(connection: Connection, game: Game):
    """Insert a new game into database from game object"""
    insert_game = ("INSERT INTO game "
                   "(id, season_month_id, type, game_date, game_time, visitor_team_id, home_team_id, visitor_point, home_point) "
                   "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data_game = (game.id, game.season_month_id, game.type, game.game_date, game.game_time, game.visitor_team_id,
                 game.home_team_id, game.visitor_point, game.home_point)
    DataBase.execute(connection, insert_game, data_game)


def delete_game(connection: Connection, game_id: str):
    """Delete the game from database"""
    query = "DELETE FROM game " \
            "WHERE id='" + str(game_id) + "'"
    DataBase.execute(connection, query)


def add_game_visitor_players(connection: Connection, game_id: str,
                             players: tuple[list[Player | PlayerHist], list[int]]):
    """Insert all visitor player relation with a game into database"""
    insert_game_visitor_player = ("INSERT INTO game_visitor_player "
                                  "(id, game_id, player_id, mp) "
                                  "VALUES (%s, %s, %s, %s)")
    for i in range(len(players[0])):
        game_visitor_player = None
        player = players[0][i]
        mp = players[1][i]

        if type(player).__name__ == "Player":
            game_visitor_player = GameVisitorPlayer(game_id, player.id, mp)
        elif type(player).__name__ == "PlayerHist":
            game_visitor_player = GameVisitorPlayer(game_id, player.player_id, mp)

        data_game_visitor_player = (game_visitor_player.id, game_visitor_player.game_id, game_visitor_player.player_id,
                                    game_visitor_player.mp)
        DataBase.execute(connection, insert_game_visitor_player, data_game_visitor_player)


def add_game_home_players(connection: Connection, game_id: str,
                          players: tuple[list[Player | PlayerHist], list[int]]):
    """Insert all home player relation with a game into database"""
    insert_game_home_player = ("INSERT INTO game_home_player "
                               "(id, game_id, player_id, mp) "
                               "VALUES (%s, %s, %s, %s)")
    for i in range(len(players[0])):
        game_home_player = None
        player = players[0][i]
        mp = players[1][i]

        if type(player).__name__ == "Player":
            game_home_player = GameHomePlayer(game_id, player.id, mp)
        elif type(player).__name__ == "PlayerHist":
            game_home_player = GameHomePlayer(game_id, player.player_id, mp)

        data_game_home_player = (game_home_player.id, game_home_player.game_id, game_home_player.player_id,
                                 game_home_player.mp)
        DataBase.execute(connection, insert_game_home_player, data_game_home_player)


def get_visitor_players_by_game(connection: Connection, game_id: str) -> list[Player | PlayerHist]:
    """Get all visitor players that are played in the game_id"""
    query = "SELECT player_id " \
            "FROM game_visitor_player " \
            "WHERE game_id = '" + str(game_id) + "'"
    DataBase.execute(connection, query)
    visitor_players = connection.cursor.fetchall()
    return [player[0] for player in visitor_players]


def get_home_players_by_game(connection: Connection, game_id: str) -> list[Player | PlayerHist]:
    """Get all visitor players that are played in the game_id"""
    query = "SELECT player_id " \
            "FROM game_home_player " \
            "WHERE game_id = '" + str(game_id) + "'"
    DataBase.execute(connection, query)
    home_players = connection.cursor.fetchall()
    return [player[0] for player in home_players]


def get_games_to_update_score(connection: Connection) -> list[Game]:
    """Get all games already played that haven't been updated"""
    query = "SELECT id, season_month_id, type, game_date, game_time, visitor_team_id, home_team_id, visitor_point, home_point " \
            "FROM game " \
            "WHERE visitor_point=0 and home_point=0 and CONCAT(game_date, ' ', game_time)<DATE_SUB(NOW(), INTERVAL 8 HOUR) " \
            "ORDER BY game_date ASC, game_time ASC"
    DataBase.execute(connection, query)
    games = connection.cursor.fetchall()
    return [Game(game[0], game[1], game[2], game[3], game[4], game[5], game[6], game[7], game[8]) for game in games]


def update_game_score_and_type(connection: Connection, game: Game):
    """Update the visitor and home points in a game"""
    update_game = ("UPDATE game "
                   "SET visitor_point=%s, home_point=%s, type=%s "
                   "WHERE (id=%s)")
    data_game = (game.visitor_point, game.home_point, game.type, game.id)
    DataBase.execute(connection, update_game, data_game)


def update_game_time(connection: Connection, game: Game):
    """Update the time game"""
    update_game = ("UPDATE game "
                   "SET game_time=%s "
                   "WHERE (id=%s)")
    data_game = (game.game_time, game.id)
    DataBase.execute(connection, update_game, data_game)


def get_game(connection: Connection, game_id: str) -> Game | None:
    """Get the game with id = game_id"""
    query = "SELECT id, season_month_id, type, game_date, game_time, visitor_team_id, home_team_id, visitor_point, home_point " \
            "FROM game " \
            "WHERE id='" + str(game_id) + "'"
    DataBase.execute(connection, query)
    game = connection.cursor.fetchone()
    if game is None:
        return None
    else:
        return Game(game[0], game[1], game[2], game[3], game[4], game[5], game[6], game[7], game[8])


def get_games_by_season_month(connection: Connection, season_month_id: int) -> list[Game]:
    """Get ALL games saved in a specific month of a season"""
    query = "SELECT id, season_month_id, type, game_date, game_time, visitor_team_id, home_team_id, visitor_point, home_point " \
            "FROM game " \
            "WHERE season_month_id=" + str(season_month_id)
    DataBase.execute(connection, query)
    games = connection.cursor.fetchall()
    return [Game(game[0], game[1], game[2], game[3], game[4], game[5], game[6], game[7], game[8]) for game in games]


def get_games_id_by_season_month(connection: Connection, season_month_id: int) -> list[Game]:
    """Get ALL games id saved in a specific month of a season"""
    query = "SELECT id " \
            "FROM game " \
            "WHERE season_month_id=" + str(season_month_id)
    DataBase.execute(connection, query)
    games = connection.cursor.fetchall()
    return [game[0] for game in games]


def get_games_without_time(connection: Connection) -> list[Game]:
    """Get ALL games saved without time"""
    query = "SELECT id, season_month_id, type, game_date, game_time, visitor_team_id, home_team_id, visitor_point, home_point " \
            "FROM game " \
            "WHERE game_time IS null " \
            "ORDER BY game_date ASC"
    DataBase.execute(connection, query)
    games = connection.cursor.fetchall()
    return [Game(game[0], game[1], game[2], game[3], game[4], game[5], game[6], game[7], game[8]) for game in games]


def get_number_season_games(connection: Connection, season_id: int) -> int:
    """Get number of games in a specific season"""
    query = ("SELECT count(*) "
             "FROM game "
             "WHERE season_month_id IN (select id from season_month where season_id=" + str(season_id) + ")")
    DataBase.execute(connection, query)
    return int(connection.cursor.fetchone()[0])


def save_prediction(connection, game_id: str, team_winner: str):
    """Save the prediction (who team is the winner) in the game"""
    update_game = ("UPDATE game "
                   "SET prediction_id=%s "
                   "WHERE (id=%s)")
    data_game = (str(team_winner), str(game_id))
    DataBase.execute(connection, update_game, data_game)


def delete_visitor_players_from_season(connection: Connection, season_id: int):
    """Remove all game_visitor_player from the season"""
    delete_visitor_player = ("DELETE FROM game_visitor_player "
                             "WHERE game_id IN "
                             "(SELECT id FROM game WHERE season_month_id IN "
                             "(SELECT id FROM season_month WHERE season_id=" + str(season_id) + "))")
    DataBase.execute(connection, delete_visitor_player)


def delete_home_players_from_season(connection: Connection, season_id: int):
    """Remove all game_home_player from the season"""
    delete_home_player = ("DELETE FROM game_home_player "
                          "WHERE game_id IN "
                          "(SELECT id FROM game WHERE season_month_id IN "
                          "(SELECT id FROM season_month WHERE season_id=" + str(season_id) + "))")
    DataBase.execute(connection, delete_home_player)


def delete_games_from_season(connection: Connection, season_id: int):
    """Remove all games from the season"""
    delete_games = ("DELETE FROM game "
                    "WHERE season_month_id IN "
                    "(SELECT id FROM season_month WHERE season_id=" + str(season_id) + ")")
    DataBase.execute(connection, delete_games)
