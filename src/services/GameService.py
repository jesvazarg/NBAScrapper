from bs4 import BeautifulSoup

from NBAScrapper.src.repository import SeasonRepository, GameRepository
from NBAScrapper.src.domain.Game import Game
from NBAScrapper.src.domain.Player import Player
from NBAScrapper.src.domain.PlayerHist import PlayerHist
from NBAScrapper.src.domain.SeasonMonth import SeasonMonth
from NBAScrapper.src.services import PlayService, PlayerService, TeamService
from NBAScrapper.src.utils import DataBase, BS4Connection, URLs, Log
from NBAScrapper.src.utils.DataBase import Connection


def insert_new_games(connection: Connection, season_month: SeasonMonth) -> bool:
    """Insert all games from a season month into database"""
    is_saved_finished = False
    current_season = SeasonRepository.get_current_season(connection)
    is_current_season = current_season == season_month.season_id

    game_id_list = GameRepository.get_games_id_by_season_month(connection, season_month.id)
    if len(game_id_list) == 0:
        Log.log_info(str(season_month.season_id), "Saving games from month " + season_month.month +
                     " of season " + str(season_month.season_id))

    soup = BS4Connection.init_bs4(URLs.get_url_games(str(season_month.season_id), season_month.month.lower()))
    soup_game_list = soup.tbody.find_all("tr")

    # Check if not all saved games saved to go through all games of the corresponding season and month
    if len(game_id_list) != len(soup_game_list):
        for soup_game in soup_game_list:
            soup_date = soup_game.th.a
            # If the game has a date
            if soup_date is not None:
                game_id = soup_game.th.get("csk")
                # Check the game is not saved
                if game_id not in game_id_list:
                    # Search game date and time
                    # First calculate the date
                    game_time = None
                    day_month_year = soup_date.get("href").split("month=")[1].split("&day=")
                    month = day_month_year[0]
                    day = day_month_year[1].split("&year=")[0]
                    year = day_month_year[1].split("&year=")[1]
                    date = year + "-" + month + "-" + day
                    game_date = date
                    # Later calculate the time if it is exists
                    if soup_game.td.string is not None:
                        game_time = apply_time_format(soup_game.td.string)

                    # Game type
                    table_notes = soup_game.find("td", attrs={"data-stat": "game_remarks"}).string
                    # Not all seasons have Play-in
                    if table_notes is not None and "play-in" in table_notes.lower():
                        game_type = "PI"
                    else:
                        number_games = GameRepository.get_number_season_games(connection, season_month.season_id)
                        number_teams = TeamService.get_number_teams(connection, season_month.season_id,
                                                                    is_current_season)
                        # Number of games in the season = 82 * number of teams
                        if number_games > (82 * number_teams / 2):
                            game_type = "PO"
                        else:
                            game_type = "SE"

                    # Visiting team
                    visitor_team_old_id = soup_game.td.next_sibling.get("csk")[0:3]
                    visitor_team = TeamService.get_team_by_ids(connection, visitor_team_old_id, season_month.season_id)
                    if visitor_team is None:
                        Log.log_error(str(season_month.season_id),
                                      visitor_team_old_id + " id team not found in game id: " + game_id)

                    # Visiting team point
                    visitor_point = soup_game.td.next_sibling.next_sibling.string
                    if visitor_point is None:
                        visitor_point = 0
                    else:
                        visitor_point = int(visitor_point)

                    # Home team
                    home_team_old_id = soup_game.td.next_sibling.next_sibling.next_sibling.get("csk")[0:3]
                    home_team = TeamService.get_team_by_ids(connection, home_team_old_id, season_month.season_id)
                    if home_team is None:
                        Log.log_error(str(season_month.season_id),
                                      home_team_old_id + " id team not found in game id: " + game_id)

                    # Home team point
                    home_point = soup_game.td.next_sibling.next_sibling.next_sibling.next_sibling.string
                    if home_point is None:
                        home_point = 0
                    else:
                        home_point = int(home_point)

                    # Points will be added when the plays are registered
                    game = Game(game_id, season_month.id, game_type, game_date, game_time,
                                visitor_team.id, home_team.id)
                    # Add the game to be able to make associations
                    GameRepository.add_game(connection, game)
                    DataBase.commit(connection)
                    Log.log_info(str(season_month.season_id), " + Added a new " + str(game))

                    # Game players
                    if visitor_point != 0 and home_point != 0:
                        # If game is played, search the players who have participated in both teams
                        soup_players = BS4Connection.init_bs4(URLs.get_url_game_bs(game_id))

                        # Update game type
                        game = update_game_type(game, soup_players, season_month.season_id)

                        # Visiting team players
                        visitor_players = get_game_players_list(connection, visitor_team.id, visitor_team_old_id,
                                                                season_month.season_id, soup_players, is_current_season,
                                                                True)
                        # Home team players
                        home_players = get_game_players_list(connection, home_team.id, home_team_old_id,
                                                             season_month.season_id, soup_players, is_current_season,
                                                             True)

                        no_played = get_game_players_list(connection, visitor_team.id, visitor_team_old_id,
                                                          season_month.season_id, soup_players, is_current_season,
                                                          False)[0] + \
                                    get_game_players_list(connection, home_team.id, home_team_old_id,
                                                          season_month.season_id, soup_players, is_current_season,
                                                          False)[0]

                        # Add players who have played
                        GameRepository.add_game_visitor_players(connection, game.id, visitor_players)
                        GameRepository.add_game_home_players(connection, game.id, home_players)

                        # Add the plays and update the game stats
                        game = PlayService.save_game_details(connection, game, visitor_players[0], home_players[0],
                                                             no_played, is_current_season)
                        DataBase.commit(connection)
                        Log.log_info(str(season_month.season_id),
                                     " + Add visitor players, home players and plays of the game " + game.id)
                        Log.log_info(str(season_month.season_id), " * Update the score game " + str(game))

        Log.log_info(str(season_month.season_id), "All GAMES from month " + season_month.month +
                     " of season " + str(season_month.season_id) + " have been saved successfully")
        is_saved_finished = True

    return is_saved_finished


def update_games(connection: Connection):
    """Update game time and game score"""
    # Update game time
    update_time(connection)

    # Get games to update score
    games = GameRepository.get_games_to_update_score(connection)
    for game in games:
        # Update game score
        game_updated = update_game_score(connection, game)
        if game_updated is not None:
            DataBase.commit(connection)
            season_month = SeasonRepository.get_season_month_by_id(connection, game_updated.season_month_id)
            Log.log_info(str(season_month.season_id), " * Update the score " + str(game_updated))


def update_game_score(connection: Connection, game: Game) -> Game | None:
    """Add players to game and update game score and stats"""
    game_updated = None
    season_month_game = SeasonRepository.get_season_month_by_id(connection, game.season_month_id)
    Log.create_logging(str(season_month_game.season_id))

    # Search players who have played in both teams
    soup_game = BS4Connection.init_bs4(URLs.get_url_game_bs(game.id))

    if soup_game is not None:
        # Update game type
        game = update_game_type(game, soup_game, season_month_game.season_id)

        # Get old id team
        visitor_team_old_id = soup_game.find(class_="scorebox").div.div.strong.a.get("href")[7:10]
        home_team_old_id = soup_game.find(class_="scorebox").div.next_sibling.next_sibling.div.strong.a.get("href")[7:10]

        # Visiting team players
        visitor_players = GameRepository.get_visitor_players_by_game(connection, game.id)
        if len(visitor_players) == 0:
            visitor_players = get_game_players_list(connection, game.visitor_team_id, visitor_team_old_id,
                                                    season_month_game.season_id, soup_game, True, True)
            GameRepository.add_game_visitor_players(connection, game.id, visitor_players)
            visitor_players = visitor_players[0]

        # Home team players
        home_players = GameRepository.get_home_players_by_game(connection, game.id)
        if len(home_players) == 0:
            home_players = get_game_players_list(connection, game.home_team_id, home_team_old_id,
                                                 season_month_game.season_id, soup_game, True, True)
            GameRepository.add_game_home_players(connection, game.id, home_players)
            home_players = home_players[0]

        no_played = get_game_players_list(connection, game.visitor_team_id, visitor_team_old_id,
                                          season_month_game.season_id, soup_game, True, False)[0] + \
                    get_game_players_list(connection, game.home_team_id, home_team_old_id,
                                          season_month_game.season_id, soup_game, True, False)[0]

        # Game plays
        game_updated = PlayService.save_game_details(connection, game, visitor_players, home_players, no_played, True)

    return game_updated


def update_time(connection: Connection):
    """Update game time"""
    season_month = None
    soup = None
    game_date = None
    games_in_day = []
    games_without_time = GameRepository.get_games_without_time(connection)

    for game in games_without_time:

        if season_month is None or season_month.id != game.season_month_id:
            season_month = SeasonRepository.get_season_month_by_id(connection, game.season_month_id)
            soup = BS4Connection.init_bs4(URLs.get_url_games(str(season_month.season_id), season_month.month.lower()))
        if game_date is None or game_date != game.game_date:
            game_date = game.game_date
            games_in_day = soup.find_all("a", href="/boxscores/index.fcgi?month=" + str(game.game_date.month) +
                                                   "&day=" + str(game.game_date.day) +
                                                   "&year=" + str(game.game_date.year))
        for game_in_day in games_in_day:
            game_id = game_in_day.parent.get("csk")
            if game.id == game_id:
                soup_time = game_in_day.parent.parent.td.string
                if soup_time is not None:
                    game.game_time = apply_time_format(soup_time)
                    GameRepository.update_game_time(connection, game)
                    DataBase.commit(connection)
                    season_month = SeasonRepository.get_season_month_by_id(connection, game.season_month_id)
                    Log.log_info(str(season_month.season_id), " * Update the game time " + str(game))
                break


def get_game_players_list(connection: Connection, team_id: str, team_old_id: str, season_id: int,
                          soup_game: BeautifulSoup, is_current_season: bool, is_played: bool
                          ) -> tuple[list[Player | PlayerHist | str], list[int]]:
    """Get the players who have participated in both teams with the minutes played
    If is_played = False, return the id players who are in the team and haven't played"""
    player_list = []
    mp_list = []
    soup_team_players = soup_game.find(attrs={"class": "table_container",
                                              "id": "div_box-" + team_old_id + "-game-basic"}
                                       ).tbody.find_all("tr")
    for soup_player in soup_team_players:
        player_id = soup_player.th.get("data-append-csv")
        if player_id is not None:
            soup_mp = soup_player.find("td", attrs={"data-stat": "mp"})
            if soup_mp is not None and is_played:
                # Check if add player or player history
                player = PlayerService.get_or_create_player(connection, player_id, team_id, season_id,
                                                            is_current_season)

                # MP
                mp = soup_mp.string

                # Add the game in the player stat
                player.game += 1
                player.add_minutes_played(mp)
                player_list.append(player)
                mp_list.append(get_minutes_played(mp))

            elif soup_mp is None and not is_played:
                player_list.append(player_id)

    return player_list, mp_list


def get_minutes_played(time: str) -> int:
    return int(time.split(":")[0])*60 + int(time.split(":")[1])


def apply_time_format(time_text: str) -> str:
    """Apply 24H time format
    Change 07:23p TO 19:23"""
    time_moment = time_text[-1]
    time = time_text[0:-1]
    hour = int(time.split(":")[0])
    minute = int(time.split(":")[1])

    # If it is 12 hour, subtraction 12
    if hour == 12:
        hour -= 12
    # If it is PM hour, add 12 to the hour
    if time_moment == "p":
        hour += 12

    time = str(hour) + ":" + str(minute)

    return time


def update_game_type(game: Game, soup: BeautifulSoup, season_id: int) -> Game:
    """Get game type: Season, Play-In or Play-Off
    When it's Play-Off can be Conference Eastern or Western"""
    title = soup.title.string.lower()
    if "play-in" in title:
        if game.type != "PI":
            Log.log_error(str(season_id), "Game type must be PI on " + str(game))
            game.type = "PI"
    elif "conference" in title:
        if game.type != "PO":
            Log.log_error(str(season_id), "Game type must be PO on " + str(game))
            game.type = "PO"
        if "eastern" in title:
            if "first round" in title:
                game.type += "ER"
            elif "semifinals" in title:
                game.type += "ES"
            elif "finals" in title:
                game.type += "EF"
        elif "western" in title:
            if "first round" in title:
                game.type += "WR"
            elif "semifinals" in title:
                game.type += "WS"
            elif "finals" in title:
                game.type += "WF"
    elif "finals" in title:
        if game.type != "PO":
            Log.log_error(str(season_id), "Game type must be PO on " + str(game))
        game.type = "POF"
    else:
        if game.type != "SE":
            Log.log_error(str(season_id), "Game type must be SE on " + str(game))
            game.type = "SE"

    return game


def check_game_exist(game_id: str) -> bool:
    """Check the game in the game list of season month
    Return True if the game exist
    Return False if the game don't exist"""
    connection = DataBase.open_connection()

    game = GameRepository.get_game(connection, game_id)
    season_month = SeasonRepository.get_season_month_by_id(connection, game.season_month_id)

    soup = BS4Connection.init_bs4(URLs.get_url_games(str(season_month.season_id), season_month.month.lower()))
    soup_game = soup.tbody.find("th", attrs={"csk": game_id})

    DataBase.close_connection(connection)

    return soup_game is not None


def delete_game(game_id: str):
    """Delete the specific game"""
    connection = DataBase.open_connection()

    GameRepository.delete_game(connection, game_id)

    Log.log_info(str(game_id[:4]), " - Remove the game " + game_id)
    DataBase.commit(connection)

    DataBase.close_connection(connection)


def delete_games_from_season(connection: Connection, season_id: int):
    GameRepository.delete_visitor_players_from_season(connection, season_id)
    GameRepository.delete_home_players_from_season(connection, season_id)
    GameRepository.delete_games_from_season(connection, season_id)
