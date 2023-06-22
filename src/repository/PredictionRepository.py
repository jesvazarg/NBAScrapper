from NBAScrapper.src.utils import DataBase
from NBAScrapper.src.utils.DataBase import Connection


def get_games_team_last_games(connection: Connection, season: int) -> list:
    """From each game, get who win the game and get all team stats from previous games played"""
    query = "SELECT " \
            "g.id AS 'game_id', " \
            "g.visitor_team_id AS 'visitor_team', " \
            "g.home_team_id AS 'home_team', " \
            "g.game_date AS 'date', " \
            "MONTH(g.game_date) AS 'month', " \
            "s.id AS 'season', " \
            "(SELECT count(*) FROM three_pointer_play tp_v WHERE tp_v.game_id = g.id AND tp_v.team_id = g.visitor_team_id AND tp_v.hit = 1) AS 'tp_v', " \
            "(SELECT count(*) FROM three_pointer_play tpp_v1 WHERE tpp_v1.game_id = g.id AND tpp_v1.team_id = g.visitor_team_id AND tpp_v1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM three_pointer_play tpp_v2 WHERE tpp_v2.game_id = g.id AND tpp_v2.team_id = g.visitor_team_id) AS 'tpp_v', " \
            "(SELECT count(*) FROM two_pointer_play dp_v WHERE dp_v.game_id = g.id AND dp_v.team_id = g.visitor_team_id AND dp_v.hit = 1) AS 'dp_v', " \
            "(SELECT count(*) FROM two_pointer_play dpp_v1 WHERE dpp_v1.game_id = g.id AND dpp_v1.team_id = g.visitor_team_id AND dpp_v1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM two_pointer_play dpp_v2 WHERE dpp_v2.game_id = g.id AND dpp_v2.team_id = g.visitor_team_id) AS 'dpp_v', " \
            "(SELECT count(*) FROM free_throw_play ft_v WHERE ft_v.game_id = g.id AND ft_v.team_id = g.visitor_team_id AND ft_v.hit = 1) AS 'ft_v', " \
            "(SELECT count(*) FROM free_throw_play ftp_v1 WHERE ftp_v1.game_id = g.id AND ftp_v1.team_id = g.visitor_team_id AND ftp_v1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM free_throw_play ftp_v2 WHERE ftp_v2.game_id = g.id AND ftp_v2.team_id = g.visitor_team_id) AS 'ftp_v', " \
            "(SELECT count(*) FROM three_pointer_play tp_h WHERE tp_h.game_id = g.id AND tp_h.team_id = g.home_team_id AND tp_h.hit = 1) AS 'tp_h', " \
            "(SELECT count(*) FROM three_pointer_play tpp_h1 WHERE tpp_h1.game_id = g.id AND tpp_h1.team_id = g.home_team_id AND tpp_h1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM three_pointer_play tpp_h2 WHERE tpp_h2.game_id = g.id AND tpp_h2.team_id = g.home_team_id) AS 'tpp_h', " \
            "(SELECT count(*) FROM two_pointer_play dp_h WHERE dp_h.game_id = g.id AND dp_h.team_id = g.home_team_id AND dp_h.hit = 1) AS 'dp_h', " \
            "(SELECT count(*) FROM two_pointer_play dpp_h1 WHERE dpp_h1.game_id = g.id AND dpp_h1.team_id = g.home_team_id AND dpp_h1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM two_pointer_play dpp_h2 WHERE dpp_h2.game_id = g.id AND dpp_h2.team_id = g.home_team_id) AS 'dpp_h', " \
            "(SELECT count(*) FROM free_throw_play ft_h WHERE ft_h.game_id = g.id AND ft_h.team_id = g.home_team_id AND ft_h.hit = 1) AS 'ft_h', " \
            "(SELECT count(*) FROM free_throw_play ftp_h1 WHERE ftp_h1.game_id = g.id AND ftp_h1.team_id = g.home_team_id AND ftp_h1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM free_throw_play ftp_h2 WHERE ftp_h2.game_id = g.id AND ftp_h2.team_id = g.home_team_id) AS 'ftp_h', " \
            "g.visitor_point > g.home_point AS 'visitor_win' " \
            "FROM game g, season_month sm, season s " \
            "WHERE " \
            "g.season_month_id = sm.id AND " \
            "sm.season_id = s.id AND " \
            "g.visitor_point > 0 AND " \
            "g.home_point > 0 AND " \
            "g.season_month_id IN (SELECT sm1.id FROM season_month sm1 WHERE sm1.season_id IN (" \
            + str(season) + ", " + str(season - 1) + ", " + str(season - 2) + \
            ")) " \
            "ORDER BY g.game_date DESC, g.game_time DESC, g.id DESC"
    DataBase.execute(connection, query)
    return connection.cursor.fetchall()


def get_games_team_last_games_predict(connection: Connection, season: int) -> list:
    """From each game, get if the game is played and get all team stats from previous games played"""
    query = "SELECT " \
            "g.id AS 'game_id', " \
            "g.visitor_team_id AS 'visitor_team', " \
            "g.home_team_id AS 'home_team', " \
            "g.game_date AS 'date', " \
            "MONTH(g.game_date) AS 'month', " \
            "s.id AS 'season', " \
            "(SELECT count(*) FROM three_pointer_play tp_v WHERE tp_v.game_id = g.id AND tp_v.team_id = g.visitor_team_id AND tp_v.hit = 1) AS 'tp_v', " \
            "(SELECT count(*) FROM three_pointer_play tpp_v1 WHERE tpp_v1.game_id = g.id AND tpp_v1.team_id = g.visitor_team_id AND tpp_v1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM three_pointer_play tpp_v2 WHERE tpp_v2.game_id = g.id AND tpp_v2.team_id = g.visitor_team_id) AS 'tpp_v', " \
            "(SELECT count(*) FROM two_pointer_play dp_v WHERE dp_v.game_id = g.id AND dp_v.team_id = g.visitor_team_id AND dp_v.hit = 1) AS 'dp_v', " \
            "(SELECT count(*) FROM two_pointer_play dpp_v1 WHERE dpp_v1.game_id = g.id AND dpp_v1.team_id = g.visitor_team_id AND dpp_v1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM two_pointer_play dpp_v2 WHERE dpp_v2.game_id = g.id AND dpp_v2.team_id = g.visitor_team_id) AS 'dpp_v', " \
            "(SELECT count(*) FROM free_throw_play ft_v WHERE ft_v.game_id = g.id AND ft_v.team_id = g.visitor_team_id AND ft_v.hit = 1) AS 'ft_v', " \
            "(SELECT count(*) FROM free_throw_play ftp_v1 WHERE ftp_v1.game_id = g.id AND ftp_v1.team_id = g.visitor_team_id AND ftp_v1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM free_throw_play ftp_v2 WHERE ftp_v2.game_id = g.id AND ftp_v2.team_id = g.visitor_team_id) AS 'ftp_v', " \
            "(SELECT count(*) FROM three_pointer_play tp_h WHERE tp_h.game_id = g.id AND tp_h.team_id = g.home_team_id AND tp_h.hit = 1) AS 'tp_h', " \
            "(SELECT count(*) FROM three_pointer_play tpp_h1 WHERE tpp_h1.game_id = g.id AND tpp_h1.team_id = g.home_team_id AND tpp_h1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM three_pointer_play tpp_h2 WHERE tpp_h2.game_id = g.id AND tpp_h2.team_id = g.home_team_id) AS 'tpp_h', " \
            "(SELECT count(*) FROM two_pointer_play dp_h WHERE dp_h.game_id = g.id AND dp_h.team_id = g.home_team_id AND dp_h.hit = 1) AS 'dp_h', " \
            "(SELECT count(*) FROM two_pointer_play dpp_h1 WHERE dpp_h1.game_id = g.id AND dpp_h1.team_id = g.home_team_id AND dpp_h1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM two_pointer_play dpp_h2 WHERE dpp_h2.game_id = g.id AND dpp_h2.team_id = g.home_team_id) AS 'dpp_h', " \
            "(SELECT count(*) FROM free_throw_play ft_h WHERE ft_h.game_id = g.id AND ft_h.team_id = g.home_team_id AND ft_h.hit = 1) AS 'ft_h', " \
            "(SELECT count(*) FROM free_throw_play ftp_h1 WHERE ftp_h1.game_id = g.id AND ftp_h1.team_id = g.home_team_id AND ftp_h1.hit = 1) / (SELECT IF(count(*) = 0, 1, count(*)) FROM free_throw_play ftp_h2 WHERE ftp_h2.game_id = g.id AND ftp_h2.team_id = g.home_team_id) AS 'ftp_h', " \
            "g.visitor_point is null or g.home_point is null or g.visitor_point = 0 or g.home_point = 0 AS 'to_preedict' " \
            "FROM game g, season_month sm, season s " \
            "WHERE " \
            "g.season_month_id = sm.id AND " \
            "sm.season_id = s.id AND " \
            "g.season_month_id IN (SELECT sm1.id FROM season_month sm1 WHERE sm1.season_id IN (" \
            + str(season) + ", " + str(season - 1) + ", " + str(season - 2) + \
            ")) " \
            "ORDER BY g.game_date DESC, g.game_time DESC, g.id DESC"
    DataBase.execute(connection, query)
    return connection.cursor.fetchall()
