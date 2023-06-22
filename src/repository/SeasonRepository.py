from NBAScrapper.src.domain.Season import Season
from NBAScrapper.src.domain.SeasonMonth import SeasonMonth
from NBAScrapper.src.utils import DataBase
from NBAScrapper.src.utils.DataBase import Connection


def add_season(connection: Connection, season: Season):
    """Insert a new season into database from season object"""
    insert_season = ("INSERT INTO season "
                     "(id, name) "
                     "VALUES (%s, %s)")
    data_season = (season.id, season.name)
    DataBase.execute(connection, insert_season, data_season)


def get_all_seasons_id(connection: Connection) -> list[int]:
    """Get all id seasons from database"""
    query = "SELECT id " \
            "FROM season"
    DataBase.execute(connection, query)
    return [row[0] for row in connection.cursor.fetchall()]


def get_current_season(connection: Connection) -> int | None:
    """Get maximum id of teams from database"""
    query = "SELECT max(id) " \
            "FROM season"
    DataBase.execute(connection, query)
    season_id = connection.cursor.fetchone()
    if season_id is None:
        return None
    else:
        return season_id[0]


def get_oldest_season_id(connection: Connection) -> int | None:
    """Get minimum id of teams from database"""
    query = "SELECT min(id) " \
            "FROM season"
    DataBase.execute(connection, query)
    season_id = connection.cursor.fetchone()
    if season_id is None:
        return None
    else:
        return season_id[0]


def get_season(connection: Connection, season_id: int) -> Season | None:
    """Get season with id = season_id"""
    query = ("SELECT id, name "
             "FROM season "
             "WHERE id=" + str(season_id))
    DataBase.execute(connection, query)
    season = connection.cursor.fetchone()
    if season is None:
        return None
    else:
        return Season(season[0], season[1])


def get_season_month_by_month_and_season(connection: Connection, month: str, season_id: int) -> SeasonMonth | None:
    """Get SeasonMonth with month = month and season = season_id"""
    query = ("SELECT id, month, season_id "
             "FROM season_month "
             "WHERE month='" + str(month) + "' and season_id=" + str(season_id))
    DataBase.execute(connection, query)
    season_id = connection.cursor.fetchone()
    if season_id is None:
        return None
    else:
        return SeasonMonth(season_id[1], season_id[2], season_id[0])


def get_months_of_season(connection: Connection, season_id: int) -> list[SeasonMonth]:
    """Get ALL SeasonMonth from season_id"""
    query = ("SELECT id, month, season_id "
             "FROM season_month "
             "WHERE season_id=" + str(season_id))
    DataBase.execute(connection, query)
    season_month_list = connection.cursor.fetchall()
    return [SeasonMonth(season_month[1], season_month[2], season_month[0]) for season_month in season_month_list]


def get_season_month_by_id(connection: Connection, season_month_id: int) -> SeasonMonth | None:
    """Get SeasonMonth with id = season_month_id"""
    query = ("SELECT id, month, season_id "
             "FROM season_month "
             "WHERE id=" + str(season_month_id))
    DataBase.execute(connection, query)
    season_month = connection.cursor.fetchone()
    if season_month is None:
        return None
    else:
        return SeasonMonth(season_month[1], season_month[2], season_month[0])


def add_season_month(connection: Connection, season_month: SeasonMonth):
    """Create an id and insert a new SeasonMonth into database from season_month object"""
    season_month_id = int(str(season_month.season_id) +
                          str(get_number_season_month_from_season(connection, season_month.season_id)))

    insert_season_month = ("INSERT INTO season_month "
                           "(id, season_id, month) "
                           "VALUES (%s, %s, %s)")
    data_season_month = (season_month_id, season_month.season_id, season_month.month)
    DataBase.execute(connection, insert_season_month, data_season_month)


def get_number_seasons(connection: Connection) -> int:
    """Create an id to season_month in a specific season"""
    query = ("SELECT count(*) "
             "FROM season")
    DataBase.execute(connection, query)
    return int(connection.cursor.fetchone()[0])


def get_number_season_month_from_season(connection: Connection, season_id: int) -> int:
    """Create an id to season_month in a specific season"""
    query = ("SELECT count(*) "
             "FROM season_month "
             "WHERE season_id=" + str(season_id))
    DataBase.execute(connection, query)
    return int(connection.cursor.fetchone()[0])
