from os import remove

from NBAScrapper.src.repository import SeasonRepository
from NBAScrapper.src.services import SeasonService, TeamService, GameService, PredictionService, PlayService, \
    PlayerService
from NBAScrapper.src.utils import DataBase, Log, BS4Connection, URLs


def check_and_insert():
    """Main routine"""
    while 1:
        print("Starting the processor")
        Log.create_logging("connection_error")
        connection = DataBase.open_connection()

        current_season_id = SeasonService.get_current_season(connection)
        TeamService.check_and_insert(connection, current_season_id)
        number_seasons = SeasonRepository.get_number_seasons(connection)
        oldest_season = SeasonRepository.get_oldest_season_id(connection)
        if number_seasons == 1:
            GameService.update_games(connection)
            SeasonService.insert_seasons(connection, oldest_season, number_seasons)
        else:
            GameService.update_games(connection)
            SeasonService.insert_new_months(connection, current_season_id)

            if number_seasons > 3:
                has_model = PredictionService.has_model(current_season_id)
                if BS4Connection.is_full_check() or not has_model:
                    PredictionService.create_current_model(connection, current_season_id)
                    if has_model:
                        Log.log_info(str(current_season_id), " + Created a model from season " + str(current_season_id))
                PredictionService.predict_new_games(connection, current_season_id)

            # Before 1968 it changes format, then not load more seasons
            if oldest_season > 1968:
                SeasonService.insert_seasons(connection, oldest_season, number_seasons)

        DataBase.close_connection(connection)
        print("Waiting for the next day")
        BS4Connection.wait_next_day()


def test(game_id: str):
    """Function to test some operations"""
    Log.create_logging("test")

    visitor_point = 0
    home_point = 0
    while visitor_point == 0 and home_point == 0:
        soup = BS4Connection.test_bs4(URLs.get_url_game_bs(game_id))
        soup_scores = soup.find_all(class_="score")

        visitor_point = int(soup_scores[0].string)
        home_point = int(soup_scores[1].string)

        Log.log_info("test", "visitor_point: " + str(visitor_point) + ", home_point: " + str(home_point))


def delete_season_complete(season_id: int):
    Log.create_logging("connection_error")
    connection = DataBase.open_connection()

    if SeasonRepository.get_season(connection, season_id):
        print("Removing all season " + str(season_id) + " complete")
        PlayService.delete_plays_from_season(connection, season_id)
        GameService.delete_games_from_season(connection, season_id)
        PlayerService.delete_players_from_season(connection, season_id)
        TeamService.delete_teams_from_season(connection, season_id)
        SeasonService.delete_season(connection, season_id)

        DataBase.commit(connection)
        remove("src/logs/nba-" + str(season_id) + ".log")
    else:
        print("Season " + str(season_id) + " no exist")

    DataBase.close_connection(connection)


if __name__ == "__main__":
    check_and_insert()
