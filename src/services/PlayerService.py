from datetime import datetime

from NBAScrapper.src.repository import PlayerRepository
from NBAScrapper.src.domain.Player import Player
from NBAScrapper.src.domain.PlayerHist import PlayerHist
from NBAScrapper.src.utils import URLs, BS4Connection, Log, DataBase
from NBAScrapper.src.utils.DataBase import Connection


def check_and_insert(connection: Connection, team_id: str, current_season: int, is_new: bool):
    if is_new:
        Log.log_info(str(current_season), "Saving players from team " + str(team_id))

    web_player_id_list = []
    is_full_check = BS4Connection.is_full_player_check()

    # Check all players in the team
    soup = BS4Connection.init_bs4(URLs.get_url_team(team_id, str(current_season)))
    players_soup = soup.find("table", id="roster").find_all("td", attrs={"data-stat": "player"})
    for player_soup in players_soup:
        player_number = player_soup.previous_sibling.string
        # If player has no number then he isn't en the team
        if player_number is not None:
            player_id = player_soup.a.get("href")[11:-5]
            web_player_id_list.append(player_id)

            db_player = PlayerRepository.get_player(connection, player_id)
            # If player doesn't exist, create a new player
            if db_player is None:
                web_player = player_information(player_id, team_id, player_number)
                PlayerRepository.create_new_player(connection, web_player)
                Log.log_info(str(current_season), " + Added a new " + str(web_player))
            elif db_player.team_id != team_id:
                web_player = player_information(player_id, team_id, player_number)
                if db_player.team_id is not None and db_player.team_id != "":
                    player_hist = PlayerRepository.get_player_history(connection, db_player.id,
                                                                      db_player.team_id, current_season)
                    if player_hist is None:
                        player_hist = PlayerHist(db_player.id, db_player.team_id, current_season, db_player.game,
                                                 db_player.point, db_player.mp, db_player.tp, db_player.tpa,
                                                 db_player.dp, db_player.dpa, db_player.ft, db_player.fta,
                                                 db_player.orb, db_player.drb, db_player.ast, db_player.stl,
                                                 db_player.blk, db_player.tov, db_player.foul, db_player.drw)
                        PlayerRepository.add_player_history(connection, player_hist)
                        Log.log_info(str(current_season), " * Added a new " + str(player_hist))
                    else:
                        add_player_hist_stats(connection, player_hist, db_player)
                PlayerRepository.player_change_team(connection, web_player)
                Log.log_info(str(current_season), " * Update team on " + str(web_player))

            elif is_full_check:
                web_player = player_information(player_id, team_id, player_number)
                if db_player != web_player:
                    PlayerRepository.update_player_information(connection, web_player)
                    Log.log_info(str(current_season), " * Update information " + str(web_player))

    DataBase.commit(connection)

    # Team players in database
    db_player_id_list = PlayerRepository.get_all_players_id_from_team(connection, team_id)
    # Check if any team player has left
    player_to_leave = [web_player_id for web_player_id in web_player_id_list if web_player_id not in db_player_id_list]
    for player_id in player_to_leave:
        db_player = PlayerRepository.get_player(connection, player_id)
        player_hist = PlayerRepository.get_player_history(connection, db_player.id, db_player.team_id, current_season)
        if player_hist is None:
            player_hist = PlayerHist(db_player.id, db_player.team_id, current_season, db_player.game, db_player.point,
                                     db_player.mp, db_player.tp, db_player.tpa, db_player.dp, db_player.dpa,
                                     db_player.ft, db_player.fta, db_player.orb, db_player.drb, db_player.ast,
                                     db_player.stl, db_player.blk, db_player.tov, db_player.foul, db_player.drw)
            PlayerRepository.add_player_history(connection, player_hist)
            Log.log_info(str(current_season), " * Added a new " + str(player_hist))
        else:
            add_player_hist_stats(connection, player_hist, db_player)
        PlayerRepository.leave_team(connection, player_id)
        db_player.team_id = None
        Log.log_info(str(current_season), " * Update team on " + str(db_player))

    if len(player_to_leave) > 0:
        DataBase.commit(connection)

    if is_new:
        Log.log_info(str(current_season), "All PLAYERS from team " + str(team_id) + " have been saved successfully")


def player_information(player_id: str, team_id: str | None, player_number: int | None = None) -> Player:
    soup = BS4Connection.init_bs4(URLs.get_url_player(player_id))
    soup_summary = soup.find(id="info")

    # Search player's name
    player_name = soup_summary.h1.span.string

    # Search photo URL
    soup_photo = soup_summary.find(class_="media-item")
    player_photo = soup_photo.img.get("src") if soup_photo is not None else None

    # Search birthdate
    soup_dob = soup_summary.find(id="necro-birth")
    player_dob = None
    if soup_dob is not None:
        dob_str = soup_dob.get("data-birth")
        player_dob = datetime.strptime(dob_str, '%Y-%m-%d').date()

    # Search height and weight
    player_height = -1
    player_weight = -1
    soup_height_weight = soup_dob.parent.previous_sibling.previous_sibling
    for string in soup_height_weight.stripped_strings:
        if "cm" in string:
            height_weight = string[1:-3].split("cm,\xa0")
            player_height = int(height_weight[0])
            player_weight = int(height_weight[1])

    # Search position and left or right shooter
    soup_position_shoot = soup_height_weight.previous_sibling.previous_sibling
    end_position = False
    end_shoot = False
    player_position = ""
    player_shoot = None
    for string in soup_position_shoot.stripped_strings:
        if end_position:
            positions = string.replace("and", ",").split(",")
            for position in positions:
                if "Point Guard" in position:
                    player_position += "PG"
                elif "Shooting Guard" in position:
                    player_position += "SG"
                elif "Small Forward" in position:
                    player_position += "SF"
                elif "Power Forward" in position:
                    player_position += "PF"
                elif "Center" in position:
                    player_position += "CE"
            end_position = False
        if end_shoot:
            player_shoot = string
            break
        if "Position:" in string:
            end_position = True
        elif "Shoots:" in string:
            end_shoot = True

    return Player(player_id, player_name, player_number, player_photo, player_dob, player_position, player_shoot,
                  player_height, player_weight, team_id)


def start_new_season(connection: Connection, team_id: str, season_id: int):
    """Create player history for each actually player in the team_id"""

    players = PlayerRepository.get_all_players_from_team(connection, team_id)
    for player in players:
        player_history = PlayerRepository.get_player_history(connection, player.id, team_id, season_id)
        if player_history is None:
            create_and_get_player_history(player, team_id, season_id)
        else:
            add_player_hist_stats(connection, player_history, player)
            Log.log_info(str(season_id), " * Update score " + str(player))

        PlayerRepository.reset_score(connection, player.id)
        Log.log_info(str(season_id), " / Reset score " + str(player))
    DataBase.commit(connection)


def get_or_create_player(connection: Connection, player_id: str, team_id: str, season_id: int, is_current_season: bool
                         ) -> Player | PlayerHist:
    """Get player from player_id
    If it doesn't exist, create a new player and player history in the database
    If the team is different, get or create the player history"""
    player = PlayerRepository.get_player(connection, player_id)
    if player is None:
        new_player = player_information(player_id, None, None)
        create_and_get_player(new_player, season_id)
        player = get_or_create_player_hist(connection, player_id, team_id, season_id)
    elif not is_current_season or player.team_id != team_id:
        player = get_or_create_player_hist(connection, player_id, team_id, season_id)

    return player


def get_or_create_player_hist(connection: Connection, player_id: str, team_id: str, season_id: int) -> PlayerHist:
    """Get player history from player_id, team_id and season_id
        If it doesn't exist, create a new player history in the database"""
    player_hist = PlayerRepository.get_player_history(connection, player_id, team_id, season_id)
    if player_hist is None:
        player_hist = create_and_get_player_history(player_id, team_id, season_id)

    return player_hist


def create_and_get_player_history(player: str | Player, team_id: str, season_id: int) -> PlayerHist:
    """Create a new player history in the database with:
    zero score and stats if player is an id
    team score and stats if player is a Player object"""
    second_connection = DataBase.open_connection()

    player_id = None
    if type(player).__name__ == "str":
        player_id = player
    elif type(player).__name__ == "Player":
        player_id = player.id

    player_hist = PlayerHist(player_id, team_id, season_id)

    if type(player).__name__ == "Player":
        player_hist.add_player_stats(player)

    PlayerRepository.add_player_history(second_connection, player_hist)
    DataBase.commit(second_connection)
    player_hist = PlayerRepository.get_player_history(second_connection, player_id, team_id, season_id)
    Log.log_info(str(season_id), " + Added a new " + str(player_hist))

    DataBase.close_connection(second_connection)
    return player_hist


def create_and_get_player(player: Player, season_id: int) -> Player:
    """Create a new player with zero score and stats in the database"""
    second_connection = DataBase.open_connection()

    PlayerRepository.create_new_player(second_connection, player)
    DataBase.commit(second_connection)
    player = PlayerRepository.get_player(second_connection, player.id)
    Log.log_info(str(season_id), " + Added a new " + str(player))

    DataBase.close_connection(second_connection)

    return player


def remove_team_on_team_players(connection: Connection, team_id: str, season_id: int):
    """Removes the team field from each team player and create a player history"""

    players = PlayerRepository.get_all_players_id_from_team(connection, team_id)
    for player_id in players:
        player = PlayerRepository.get_player(connection, player_id)
        remove_team_on_player(connection, player, season_id)


def remove_team_on_player(connection: Connection, player: Player, season_id: int):
    """Removes the team field on the player and create a player history"""

    player_hist = PlayerRepository.get_player_history(connection, player.id, player.team_id, season_id)
    if player_hist is None:
        player_hist = PlayerHist(player.id, player.team_id, season_id, player.game, player.point, player.mp, player.tp,
                                 player.tpa, player.dp, player.dpa, player.ft, player.fta, player.orb, player.drb,
                                 player.ast, player.stl, player.blk, player.tov, player.foul, player.drw)
        PlayerRepository.add_player_history(connection, player_hist)
        Log.log_info(str(season_id), " + Added a new " + str(player_hist))
    else:
        add_player_hist_stats(connection, player_hist, player)
    PlayerRepository.leave_team(connection, player.id)
    Log.log_info(str(season_id), " - Remove " + str(player))


def update_player_score(connection: Connection, player: Player | PlayerHist, season_id: int):
    """Update player or player history score in a game in the database"""
    
    if type(player).__name__ == "Player":
        PlayerRepository.update_player_score(connection, player)
    elif type(player).__name__ == "PlayerHist":
        PlayerRepository.update_player_history_score(connection, player)
    Log.log_info(str(season_id), " * Update score " + str(player))


def add_player_hist_stats(connection: Connection, player_hist: PlayerHist, player: Player):
    """Adds the player's stats to the player history """

    player_hist.game += player.game
    player_hist.point += player.point
    player_hist.mp += player.mp
    player_hist.tp += player.tp
    player_hist.tpa += player.tpa
    player_hist.dp += player.dp
    player_hist.dpa += player.dpa
    player_hist.ft += player.ft
    player_hist.fta += player.fta
    player_hist.orb += player.orb
    player_hist.drb += player.drb
    player_hist.ast += player.ast
    player_hist.stl += player.stl
    player_hist.blk += player.blk
    player_hist.tov += player.tov
    player_hist.foul += player.foul
    player_hist.drw += player.drw

    PlayerRepository.update_player_history_score(connection, player_hist)


def delete_players_from_season(connection: Connection, season_id: int):
    PlayerRepository.delete_players_from_season(connection, season_id)
