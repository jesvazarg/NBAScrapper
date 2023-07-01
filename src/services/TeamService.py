from NBAScrapper.src.repository import TeamRepository, SeasonRepository
from NBAScrapper.src.domain.Team import Team
from NBAScrapper.src.domain.TeamHist import TeamHist
from NBAScrapper.src.services import PlayerService
from NBAScrapper.src.utils import URLs, DataBase, BS4Connection, Log
import re

from NBAScrapper.src.utils.DataBase import Connection


def get_team_by_ids(connection: Connection, id_team: str, season_id: int) -> Team:
    visitor_team = TeamRepository.get_team(connection, id_team)
    if visitor_team is None:
        teams = TeamRepository.get_teams_by_old_id(connection, id_team)
        if len(teams) > 0:
            visitor_team = teams[0]
            if len(teams) > 1:
                Log.log_warning(str(season_id), id_team + " id belongs to many teams")
        else:
            visitor_team = get_new_old_id(connection, id_team, season_id)

    return visitor_team


def check_and_insert(connection: Connection, current_season: int):
    """Insert new teams, check for any change in teams, check if any team has left"""
    web_team_id_list = []

    soup = BS4Connection.init_bs4(URLs.get_url_all_teams())
    # Search divisions
    soup_divisions = soup.find_all(class_="division")

    is_full_check = BS4Connection.is_full_check()
    if not is_full_check:
        number_web_team = sum([len(soup_division.find_all("a")) for soup_division in soup_divisions])
        number_db_team = TeamRepository.get_number_teams_current_season(connection)
        is_full_check = number_web_team != number_db_team

    for soup_division in soup_divisions:
        division = soup_division.strong.string
        # Search teams
        soup_teams = soup_division.find_all("a")
        for soup_team in soup_teams:
            team_id = soup_team.get('href')[7:-10]

            is_new = False
            if is_full_check:
                web_team_id_list.append(team_id)
                db_team = TeamRepository.get_team(connection, team_id)
                web_team = team_information(connection, team_id, division)

                # If db_team doesn't exist
                if db_team is None:
                    is_new = True
                    # Search team information
                    TeamRepository.add_team(connection, web_team)
                    Log.log_info(str(current_season), " + Added a new " + str(web_team))
                    DataBase.commit(connection)
                else:
                    # If team doesn't exist and the team information has changed
                    if web_team != db_team:
                        TeamRepository.update_team_information(connection, web_team)
                        Log.log_info(str(current_season), " * Update information " + str(web_team))
                        DataBase.commit(connection)

            # Check any player changes
            PlayerService.check_and_insert(connection, team_id, current_season, is_new)

    db_team_list = TeamRepository.get_all_teams_id(connection)
    # Check if any team has left
    teams_to_leave = [web_team_id for web_team_id in web_team_id_list if web_team_id not in db_team_list]
    for team_id in teams_to_leave:
        team = TeamRepository.get_team(connection, team_id)
        team_hist = TeamRepository.get_team_history(connection, team_id, current_season)
        if team_hist is None:
            team_hist = TeamHist(team.id, current_season, team.game, team.point, team.tp, team.tpa, team.dp,
                                 team.dpa, team.ft, team.fta, team.orb, team.drb, team.ast, team.stl, team.blk,
                                 team.tov, team.foul, team.drw)
            TeamRepository.add_team_history(connection, team_hist)
            Log.log_info(str(current_season), " + Added a new " + str(team_hist))
        else:
            add_team_hist_stats(connection, team_hist, team)

        PlayerService.remove_team_on_team_players(connection, team_id, current_season)

        TeamRepository.remove_team(connection, team_id)
        DataBase.commit(connection)
        Log.log_info(str(current_season), " - Remove " + str(team))


def team_information(connection: Connection, team_id: str, team_division: str) -> Team:
    """Get all the information from the team_id and create Team object"""
    current_season = SeasonRepository.get_current_season(connection)
    soup = BS4Connection.init_bs4(URLs.get_url_team(team_id, str(current_season)))

    # Search the URL of the logo
    soup_logo = soup.find(class_="teamlogo")
    team_logo = soup_logo.get("src") if soup_logo is not None else None

    soup_summary = soup.find(attrs={"data-template": "Partials/Teams/Summary"})
    # Search the name
    team_name = soup_summary.h1.span.next_sibling.next_sibling.string
    # Search the conference
    team_conference = None
    for string in soup_summary.p.stripped_strings:
        if "Conference" in string:
            team_conference = string.split()[0]
            break
    # Search the coach
    team_coach = soup_summary.find_all(href=re.compile("coaches"))[0].string
    # Search the arena
    soup_arena = soup_summary.find_all(string=re.compile("Arena:"))[0].parent.parent
    team_arena = None
    end = False
    for string in soup_arena.stripped_strings:
        if end:
            team_arena = string
            break
        if "Arena:" in string:
            end = True

    return Team(str(team_id), str(team_name), str(team_logo), str(team_conference), str(team_division), str(team_coach),
                str(team_arena))


def start_new_season(connection: Connection, season_id: int):
    """Create team history for each actually team"""

    teams = TeamRepository.get_all_teams(connection)
    for team in teams:
        team_history = TeamRepository.get_team_history(connection, team.id, season_id)
        if team_history is None:
            create_and_get_team_history(team, season_id)
        else:
            add_team_hist_stats(connection, team_history, team)
            Log.log_info(str(season_id), " * Update score " + str(team))
        TeamRepository.reset_score(connection, team.id)
        Log.log_info(str(season_id), " / Reset score " + str(team))
        DataBase.commit(connection)

        # Do the same with the players in the team
        PlayerService.start_new_season(connection, team.id, season_id)


def get_or_create_team_history(connection: Connection, team_id: str, season_id: int) -> TeamHist:
    """Get team history from team_id and season_id
    If it doesn't exist, create a new team history in the database"""
    
    team_history = TeamRepository.get_team_history(connection, team_id, season_id)
    if team_history is None:
        team_history = create_and_get_team_history(team_id, season_id)

    return team_history


def create_and_get_team_history(team: str | Team, season_id: int) -> TeamHist:
    """Create a new team history in the database with:
    zero score and stats if team is an id
    team score and stats if team is a Team object"""
    second_connection = DataBase.open_connection()

    team_id = None
    if type(team).__name__ == "str":
        team_id = team
    elif type(team).__name__ == "Team":
        team_id = team.id

    team_hist = TeamHist(team_id, season_id)

    if type(team).__name__ == "Team":
        team_hist.add_team_stats(team)

    TeamRepository.add_team_history(second_connection, team_hist)
    DataBase.commit(second_connection)
    team_history = TeamRepository.get_team_history(second_connection, team_id, season_id)
    Log.log_info(str(season_id), " + Added a new " + str(team_history))

    DataBase.close_connection(second_connection)
    return team_history


def update_team_score(connection: Connection, team: Team | TeamHist, season_id: int):
    """Update team or team history score in a game in the database"""
    
    if type(team).__name__ == "Team":
        TeamRepository.update_team_score(connection, team)
    elif type(team).__name__ == "TeamHist":
        TeamRepository.update_team_history_score(connection, team)
    Log.log_info(str(season_id), " * Update score " + str(team))


def get_number_teams(connection: Connection, season_id: int, is_current_season: bool) -> int:
    """Get number of teams in the season"""

    if is_current_season:
        return TeamRepository.get_number_teams_current_season(connection)
    else:
        return TeamRepository.get_number_teams_season(connection, season_id)


def add_team_hist_stats(connection: Connection, team_hist: TeamHist, team: Team):
    """Adds the team's stats to the team history """

    team_hist.game += team.game
    team_hist.point += team.point
    team_hist.tp += team.tp
    team_hist.tpa += team.tpa
    team_hist.dp += team.dp
    team_hist.dpa += team.dpa
    team_hist.ft += team.ft
    team_hist.fta += team.fta
    team_hist.orb += team.orb
    team_hist.drb += team.drb
    team_hist.ast += team.ast
    team_hist.stl += team.stl
    team_hist.blk += team.blk
    team_hist.tov += team.tov
    team_hist.foul += team.foul
    team_hist.drw += team.drw

    TeamRepository.update_team_history_score(connection, team_hist)


def get_new_old_id(connection: Connection, old_id: str, season_id: int) -> Team:

    soup = BS4Connection.init_bs4(URLs.get_url_team(old_id, str(season_id)))
    prev_id = soup.find(class_="button2 next").parent.get("href")[7:10]

    team = TeamRepository.get_team(connection, prev_id)
    if team is not None:
        TeamRepository.add_old_id(connection, team, old_id)
        return team
    else:
        teams = TeamRepository.get_teams_by_old_id(connection, prev_id)
        if len(teams) > 0:
            if len(teams) > 1:
                Log.log_warning(str(season_id), prev_id + " id belongs to many teams")
            TeamRepository.add_old_id(connection, teams[0], old_id)
            return teams[0]
        else:
            return None


def delete_teams_from_season(connection: Connection, season_id: int):
    TeamRepository.delete_teams_from_season(connection, season_id)
