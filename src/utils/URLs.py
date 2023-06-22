HTML = ".html"
URL_ALL_SEASONS = "https://www.basketball-reference.com/leagues/"
URL_SEASON = "https://www.basketball-reference.com/leagues/NBA_VAR_YEAR_games.html"
URL_SEASON_MONTH = "https://www.basketball-reference.com/leagues/NBA_VAR_YEAR_games-VAR_MONTH.html"
URL_ALL_TEAMS = "https://www.basketball-reference.com/teams/"
URL_TEAM = "https://www.basketball-reference.com/teams/VAR_TEAM/VAR_YEAR.html"
URL_PLAYER = "https://www.basketball-reference.com/players/VAR_LETTER/VAR_PLAYER.html"
URL_GAMES = "https://www.basketball-reference.com/leagues/NBA_VAR_YEAR_games-VAR_MONTH.html"
URL_GAME_BS = "https://www.basketball-reference.com/boxscores/VAR_GAME.html"
URL_GAME_PBP = "https://www.basketball-reference.com/boxscores/pbp/VAR_GAME.html"


def get_url_all_seasons() -> str:
    """Get the URL with all seasons"""
    return URL_ALL_SEASONS


def get_url_season(year: str) -> str:
    """Get the URL with the specific seasons year to get their months"""
    return URL_SEASON.replace("VAR_YEAR", year)


def get_url_all_teams() -> str:
    """Get the URL with all teams"""
    return URL_ALL_TEAMS


def get_url_team(team_id: str, year: str) -> str:
    """Get the URL with the specific team"""
    return URL_TEAM.replace("VAR_TEAM", team_id).replace("VAR_YEAR", year)


def get_url_player(player_id: str) -> str:
    """Get the URL with the specific player to get her information"""
    player_letter = player_id[0]
    return URL_PLAYER.replace("VAR_LETTER", player_letter).replace("VAR_PLAYER", player_id)


def get_url_games(year: str, month: str) -> str:
    """Get the URL with the specific month of year to get their games"""
    return URL_GAMES.replace("VAR_YEAR", year).replace("VAR_MONTH", month)


def get_url_game_bs(game_id: str) -> str:
    """Get the URL with the specific game to get her information"""
    return URL_GAME_BS.replace("VAR_GAME", game_id)


def get_url_game_pbp(game_id: str) -> str:
    """Get the URL with the specific game to get her plays"""
    return URL_GAME_PBP.replace("VAR_GAME", game_id)
