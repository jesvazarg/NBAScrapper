from NBAScrapper.src.repository import SeasonRepository
from NBAScrapper.src.services import SeasonService, TeamService, GameService, PredictionService
from NBAScrapper.src.utils import DataBase, Log, BS4Connection, URLs


def check_and_insert():
    """Main routine"""
    while 1:
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
                    PredictionService.create_gridmodel_and_predict(connection, current_season_id)
                    if has_model:
                        Log.log_info(str(current_season_id), " + Created a model from season " + str(current_season_id))
                else:
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


if __name__ == "__main__":
    # test("202305110PHI")
    check_and_insert()
