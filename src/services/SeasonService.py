from NBAScrapper.src.repository import SeasonRepository
from NBAScrapper.src.domain.Season import Season
from NBAScrapper.src.domain.SeasonMonth import SeasonMonth
from NBAScrapper.src.services import GameService, TeamService, PredictionService
from NBAScrapper.src.utils import URLs, DataBase, BS4Connection, Log
import re

from NBAScrapper.src.utils.DataBase import Connection


def get_current_season(connection: Connection) -> int:
    """Insert the last season in the database only if run for the first time (if there is no season in the database)"""
    db_current_season_id = SeasonRepository.get_current_season(connection)

    soup = BS4Connection.init_bs4(URLs.get_url_all_seasons())
    list_seasons = soup.find(class_=["inactive"]).li.next_sibling.next_sibling.find_all('a', href=re.compile("NBA"))
    current_season_id = int(list_seasons[0].get('href')[-9:-5])

    Log.create_logging(str(current_season_id))

    # No seasons in database or there is a new current season
    if db_current_season_id is None or db_current_season_id != current_season_id:
        # When db_current_season_id != current_season_id
        if db_current_season_id is not None:
            Log.create_logging(str(db_current_season_id))
            Log.log_info(str(db_current_season_id), "NEW SEASON HAS BEEN CREATED")
            Log.log_info(str(db_current_season_id), "Creating and updating teams and players history")
            # Send to start_new_season the old current season saved in db
            TeamService.start_new_season(connection, db_current_season_id)

        current_season_name = list_seasons[0].string

        current_season = Season(current_season_id, current_season_name)
        SeasonRepository.add_season(connection, current_season)

        DataBase.commit(connection)
        Log.log_info(str(current_season_id), " + Added a new " + str(current_season))

    return current_season_id


def insert_seasons(connection: Connection, oldest_season: int, number_seasons: int):
    """Insert all seasons in the database and check the last season registered
    For each season call insert_new_months function"""
    soup = BS4Connection.init_bs4(URLs.get_url_all_seasons())
    list_seasons = soup.find(class_=["inactive"]).li.next_sibling.next_sibling.find_all('a', href=re.compile("NBA"))

    is_first_season = True

    # Look every season to save them
    for season_soup in list_seasons:
        season_id = int(season_soup.get('href')[-9:-5])

        if is_first_season:
            number_season_month = SeasonRepository.get_months_of_season(connection, season_id)
            # If number_season_month = 0, then it's a new current season
            if number_season_month == 0:
                insert_new_months(connection, season_id)
            is_first_season = False

        # Check if the season is already registered
        if season_id < oldest_season:
            Log.create_logging(str(season_id))

            season_name = season_soup.string
            season = Season(season_id, season_name)
            SeasonRepository.add_season(connection, season)

            DataBase.commit(connection)
            Log.log_info(str(season_id), " + Added a new " + str(season_id))

            # Insert the month in the season
            insert_new_months(connection, season_id)

            if number_seasons > 2:
                PredictionService.create_gridmodel_and_predict(connection, season_id + 2)
                Log.log_info(str(season_id), " + Created a model from season " + str(season_id))

            break

        # Check if any data is missing in the first season already registered
        elif season_id == oldest_season:
            Log.create_logging(str(season_id))
            insert_new_months(connection, season_id)

            if number_seasons > 2:
                PredictionService.create_gridmodel_and_predict(connection, season_id + 2)
                Log.log_info(str(season_id), " + Created a model from season " + str(season_id))


def insert_new_months(connection: Connection, season_id: int):
    """Insert all months of the season_id in the database
    and call insert_new_games function"""

    season_month_list = SeasonRepository.get_months_of_season(connection, season_id)
    if len(season_month_list) == 0:
        Log.log_info(str(season_id), "Saving MONTHS of season " + str(season_id))
    month_list = [month.month for month in season_month_list]

    soup = BS4Connection.init_bs4(URLs.get_url_season(str(season_id)))
    month_soup_list = soup.find(class_=["filter"]).find_all('a')

    # Check if all months are saved
    if len(season_month_list) == len(month_soup_list):
        # Check if all games from last month are saved
        is_saved_finished = GameService.insert_new_games(connection, season_month_list[len(season_month_list)-1])
    else:
        index = 0
        last_month_checked = False
        # Look every month
        for season_soup in month_soup_list:
            month = season_soup.string.lower().replace(" ", "-")
            # Check if the month is not saved
            if month not in month_list:
                # Check the last month already registered
                if len(month_list) > 0 and not last_month_checked:
                    GameService.insert_new_games(connection, season_month_list[index - 1])

                season_month = SeasonMonth(month, season_id)
                SeasonRepository.add_season_month(connection, season_month)

                DataBase.commit(connection)
                season_month = SeasonRepository.get_season_month_by_month_and_season(connection, month, season_id)
                Log.log_info(str(season_id), " + Added a new " + str(season_month))

                # Check the games
                GameService.insert_new_games(connection, season_month)

                last_month_checked = True
            index += 1
        is_saved_finished = True

    if is_saved_finished:
        Log.log_info(str(season_id), "All MONTHS of season " + str(season_id) + " have been saved successfully")
