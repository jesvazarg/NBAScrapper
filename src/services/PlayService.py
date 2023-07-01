import re
from functools import reduce
from bs4 import BeautifulSoup

from NBAScrapper.src.repository import PlayRepository, TeamRepository, GameRepository, SeasonRepository
from NBAScrapper.src.domain.Game import Game
from NBAScrapper.src.domain.Player import Player
from NBAScrapper.src.domain.PlayerHist import PlayerHist
from NBAScrapper.src.domain.SubstitutionPlay import SubstitutionPlay
from NBAScrapper.src.domain.ThreePointerPlay import ThreePointerPlay
from NBAScrapper.src.domain.TwoPointerPlay import TwoPointerPlay
from NBAScrapper.src.domain.FreeThrowPlay import FreeThrowPlay
from NBAScrapper.src.domain.ReboundPlay import ReboundPlay
from NBAScrapper.src.domain.TurnoverPlay import TurnoverPlay
from NBAScrapper.src.domain.FoulPlay import FoulPlay
from NBAScrapper.src.domain.Play import Play
from NBAScrapper.src.enum.ReboundType import ReboundType
from NBAScrapper.src.services import TeamService, PlayerService
from NBAScrapper.src.utils import BS4Connection, URLs, Log
from NBAScrapper.src.utils.DataBase import Connection


def save_game_details(connection: Connection, game: Game, visitor_players: list[Player | PlayerHist],
                      home_players: list[Player | PlayerHist], no_played: list[str], is_current_season: bool
                      ) -> Game | None:
    """Get and save all game plays and update players, teams and game stats and score"""
    is_substitution_active = False

    # Get current season and check if the game is played in current season
    game_season_month = SeasonRepository.get_season_month_by_id(connection, game.season_month_id)

    soup = BS4Connection.init_bs4(URLs.get_url_game_pbp(game.id))

    if soup is None:
        return None
    else:
        # Get visitor team and check if the team o team history has to be added
        if is_current_season:
            visitor_team = TeamRepository.get_team(connection, game.visitor_team_id)
        else:
            visitor_team = TeamService.get_or_create_team_history(connection, game.visitor_team_id,
                                                                  game_season_month.season_id)
        visitor_team.game += 1

        # NOT WORKING because Not all changes appear in the web
        if is_substitution_active:
            [visitor_players[i].start_game() for i in range(0, 5)]

        # # Get home team and check if the team o team history has to be added
        if is_current_season:
            home_team = TeamRepository.get_team(connection, game.home_team_id)
        else:
            home_team = TeamService.get_or_create_team_history(connection, game.home_team_id,
                                                               game_season_month.season_id)
        home_team.game += 1

        # NOT WORKING because Not all changes appear in the web
        if is_substitution_active:
            [home_players[i].start_game() for i in range(0, 5)]

        # Get play list
        play_list = soup.find_all(id="div_pbp")[0].table.find_all('td')  # Get information from play table

        tree_points_count = 0
        two_points_count = 0
        free_throw_count = 0
        rebound_count = 0
        turnover_count = 0
        foul_count = 0
        substitution_count = 0
        quarter = 1
        time = -1
        is_quarter_finished = False
        column = 1  # table column
        for ele in play_list:
            if column == 1:
                # Time
                time = str(ele.string)[:-2]  # Remove the tenths of a second (no used)
                text_quarter_finished = str(ele.next_sibling.next_sibling.string) \
                    if ele.next_sibling.next_sibling is not None else None
                is_quarter_finished = text_quarter_finished[:6] == "End of" \
                    if text_quarter_finished is not None else False
                if is_quarter_finished:
                    # Quarter is finished
                    quarter += 1
                    column += 2

                time = "00:" + time.zfill(5)

            elif (column == 2 or column == 6) and str(ele) != "<td> </td>" and not is_quarter_finished:
                # Text
                without_tags = re.findall(r'\>([^\<\>]*)', str(ele))  # Remove tags
                text = reduce(lambda x, y: x + ' ' + y, without_tags)

                # Team
                team = ""
                if column == 2:
                    team = game.visitor_team_id
                elif column == 6:
                    team = game.home_team_id

                # Create the play object
                play = Play(game.id, team, quarter, time, text)

                # Check play type
                # 3 points
                if "3-pt" in text:
                    tree_points = create_tree_or_two_points(play, ele, 3, game_season_month.season_id)  # Create object

                    if not tree_points.is_valid():
                        Log.log_error(str(game_season_month.season_id), "String not valid in: " + str(tree_points))
                    else:
                        # Save game, team and players stats
                        # Visiting team
                        if tree_points.team_id == game.visitor_team_id:
                            player_array = [player for player in visitor_players
                                            if (type(player).__name__ == "Player" and
                                                tree_points.player_id == player.id) or
                                            (type(player).__name__ == "PlayerHist" and
                                             tree_points.player_id == player.player_id)]
                            if len(player_array) == 1:  # Main player
                                if tree_points.hit:
                                    game.make_visitor_point(3)
                                    visitor_team.make_three_point()
                                    player_array[0].make_three_point()
                                else:
                                    visitor_team.fail_three_point()
                                    player_array[0].fail_three_point()
                            else:
                                Log.log_warning(str(game_season_month.season_id),
                                                "Selection main player in the play " + str(ele))
                            if tree_points.assist_id is not None:  # Assist player
                                assist_array = [player for player in visitor_players
                                                if (type(player).__name__ == "Player" and
                                                    tree_points.assist_id == player.id) or
                                                (type(player).__name__ == "PlayerHist" and
                                                 tree_points.assist_id == player.player_id)]
                                if len(assist_array) == 1:
                                    visitor_team.make_assist()
                                    assist_array[0].make_assist()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection assist player in the play " + str(ele))
                            if tree_points.block_id is not None:  # Block player
                                block_array = [player for player in home_players
                                               if (type(player).__name__ == "Player" and
                                                   tree_points.block_id == player.id) or
                                               (type(player).__name__ == "PlayerHist" and
                                                tree_points.block_id == player.player_id)]
                                if len(block_array) == 1:
                                    home_team.make_block()
                                    block_array[0].make_block()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection block player in the play " + str(ele))
                        # Home team
                        elif tree_points.team_id == game.home_team_id:
                            player_array = [player for player in home_players
                                            if (type(player).__name__ == "Player" and
                                                tree_points.player_id == player.id) or
                                            (type(player).__name__ == "PlayerHist" and
                                             tree_points.player_id == player.player_id)]
                            if len(player_array) == 1:  # Main player
                                if tree_points.hit:
                                    game.make_home_point(3)
                                    home_team.make_three_point()
                                    player_array[0].make_three_point()
                                else:
                                    home_team.fail_three_point()
                                    player_array[0].fail_three_point()
                            else:
                                Log.log_warning(str(game_season_month.season_id),
                                                "Selection main player in the play " + str(ele))
                            if tree_points.assist_id is not None:  # Assist player
                                assist_array = [player for player in home_players
                                                if (type(player).__name__ == "Player" and
                                                    tree_points.assist_id == player.id) or
                                                (type(player).__name__ == "PlayerHist" and
                                                 tree_points.assist_id == player.player_id)]
                                if len(assist_array) == 1:
                                    home_team.make_assist()
                                    assist_array[0].make_assist()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection assist player in the play " + str(ele))
                            if tree_points.block_id is not None:  # Block player
                                block_array = [player for player in visitor_players
                                               if (type(player).__name__ == "Player" and
                                                   tree_points.block_id == player.id) or
                                               (type(player).__name__ == "PlayerHist" and
                                                tree_points.block_id == player.player_id)]
                                if len(block_array) == 1:
                                    visitor_team.make_block()
                                    block_array[0].make_block()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection block player in the play " + str(ele))

                        PlayRepository.add_tree_points(connection, tree_points, tree_points_count)  # Save play
                        tree_points_count += 1

                # 2 points
                elif "2-pt" in text:
                    two_points = create_tree_or_two_points(play, ele, 2, game_season_month.season_id)  # Create object

                    if not two_points.is_valid():
                        Log.log_error(str(game_season_month.season_id), "String not valid in: " + str(two_points))
                    else:
                        # Save game, team and players stats
                        # Visiting team
                        if two_points.team_id == game.visitor_team_id:
                            player_array = [player for player in visitor_players
                                            if (type(player).__name__ == "Player" and
                                                two_points.player_id == player.id) or
                                            (type(player).__name__ == "PlayerHist" and
                                             two_points.player_id == player.player_id)]
                            if len(player_array) == 1:  # Main player
                                if two_points.hit:
                                    game.make_visitor_point(2)
                                    visitor_team.make_two_point()
                                    player_array[0].make_two_point()
                                else:
                                    visitor_team.fail_two_point()
                                    player_array[0].fail_two_point()
                            else:
                                Log.log_warning(str(game_season_month.season_id),
                                                "Selection main player in the play " + str(ele))
                            if two_points.assist_id is not None:  # Assist player
                                assist_array = [player for player in visitor_players
                                                if (type(player).__name__ == "Player" and
                                                    two_points.assist_id == player.id) or
                                                (type(player).__name__ == "PlayerHist" and
                                                 two_points.assist_id == player.player_id)]
                                if len(assist_array) == 1:
                                    visitor_team.make_assist()
                                    assist_array[0].make_assist()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection assist player in the play " + str(ele))
                            if two_points.block_id is not None:  # Block player
                                block_array = [player for player in home_players
                                               if (type(player).__name__ == "Player" and
                                                   two_points.block_id == player.id) or
                                               (type(player).__name__ == "PlayerHist" and
                                                two_points.block_id == player.player_id)]
                                if len(block_array) == 1:
                                    home_team.make_block()
                                    block_array[0].make_block()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection block player in the play " + str(ele))

                        # Home team
                        elif two_points.team_id == game.home_team_id:
                            player_array = [player for player in home_players
                                            if (type(player).__name__ == "Player" and
                                                two_points.player_id == player.id) or
                                            (type(player).__name__ == "PlayerHist" and
                                             two_points.player_id == player.player_id)]
                            if len(player_array) == 1:  # Main player
                                if two_points.hit:
                                    game.make_home_point(2)
                                    home_team.make_two_point()
                                    player_array[0].make_two_point()
                                else:
                                    home_team.fail_two_point()
                                    player_array[0].fail_two_point()
                            else:
                                Log.log_warning(str(game_season_month.season_id),
                                                "Selection main player in the play " + str(ele))
                            if two_points.assist_id is not None:  # Assist player
                                assist_array = [player for player in home_players
                                                if (type(player).__name__ == "Player" and
                                                    two_points.assist_id == player.id) or
                                                (type(player).__name__ == "PlayerHist" and
                                                 two_points.assist_id == player.player_id)]
                                if len(assist_array) == 1:
                                    home_team.make_assist()
                                    assist_array[0].make_assist()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection assist player in the play " + str(ele))
                            if two_points.block_id is not None:  # Block player
                                block_array = [player for player in visitor_players
                                               if (type(player).__name__ == "Player" and
                                                   two_points.block_id == player.id) or
                                               (type(player).__name__ == "PlayerHist" and
                                                two_points.block_id == player.player_id)]
                                if len(block_array) == 1:
                                    visitor_team.make_block()
                                    block_array[0].make_block()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection block player in the play " + str(ele))

                        PlayRepository.add_two_points(connection, two_points, two_points_count)  # Save play
                        two_points_count += 1

                # Free throw
                elif "free throw" in text:
                    free_throw = create_free_throw(play, ele, game_season_month.season_id)  # Create object

                    if not free_throw.is_valid():
                        Log.log_error(str(game_season_month.season_id), "String not valid in: " + str(free_throw))
                    else:
                        # Visiting team
                        if free_throw.team_id == game.visitor_team_id:
                            player_array = [player for player in visitor_players
                                            if (type(player).__name__ == "Player" and
                                                free_throw.player_id == player.id) or
                                            (type(player).__name__ == "PlayerHist" and
                                             free_throw.player_id == player.player_id)]
                            if len(player_array) == 1:  # Main player
                                if free_throw.hit:
                                    game.make_visitor_point(1)
                                    visitor_team.make_free_throw()
                                    player_array[0].make_free_throw()
                                else:
                                    visitor_team.fail_free_throw()
                                    player_array[0].fail_free_throw()
                            else:
                                Log.log_warning(str(game_season_month.season_id),
                                                "Selection main player in the play " + str(ele))

                        # Home team
                        elif free_throw.team_id == game.home_team_id:
                            player_array = [player for player in home_players
                                            if (type(player).__name__ == "Player" and
                                                free_throw.player_id == player.id) or
                                            (type(player).__name__ == "PlayerHist" and
                                             free_throw.player_id == player.player_id)]
                            if len(player_array) == 1:  # Main player
                                if free_throw.hit:
                                    game.make_home_point(1)
                                    home_team.make_free_throw()
                                    player_array[0].make_free_throw()
                                else:
                                    home_team.fail_free_throw()
                                    player_array[0].fail_free_throw()
                            else:
                                Log.log_warning(str(game_season_month.season_id),
                                                "Selection main player in the play " + str(ele))

                        PlayRepository.add_free_throw(connection, free_throw, free_throw_count)  # Save play
                        free_throw_count += 1

                # Rebound
                elif "rebound" in text:
                    rebound = create_rebound(play, ele, game_season_month.season_id)  # Create object

                    # Visiting team
                    if rebound.team_id == game.visitor_team_id:
                        player_array = [player for player in visitor_players
                                        if (type(player).__name__ == "Player" and rebound.player_id == player.id) or
                                        (type(player).__name__ == "PlayerHist" and
                                         rebound.player_id == player.player_id)]
                        # Type
                        match rebound.type:
                            case ReboundType.OFFENSIVE.value:
                                visitor_team.make_offensive_rebound()
                                if len(player_array) == 1:
                                    player_array[0].make_offensive_rebound()
                            case ReboundType.DEFENSIVE.value:
                                visitor_team.make_defensive_rebound()
                                if len(player_array) == 1:
                                    player_array[0].make_defensive_rebound()

                    # Home team
                    elif rebound.team_id == game.home_team_id:
                        player_array = [player for player in home_players
                                        if (type(player).__name__ == "Player" and rebound.player_id == player.id) or
                                        (type(player).__name__ == "PlayerHist" and
                                         rebound.player_id == player.player_id)]
                        # Type
                        match rebound.type:
                            case ReboundType.OFFENSIVE.value:
                                home_team.make_offensive_rebound()
                                if len(player_array) == 1:
                                    player_array[0].make_offensive_rebound()
                            case ReboundType.DEFENSIVE.value:
                                home_team.make_defensive_rebound()
                                if len(player_array) == 1:
                                    player_array[0].make_defensive_rebound()

                    PlayRepository.add_rebound(connection, rebound, rebound_count)  # Save play
                    rebound_count += 1

                # Turnover
                elif "Turnover" in text:
                    turnover = create_turnover(play, ele, game_season_month.season_id)  # Create object

                    if not turnover.is_valid():
                        Log.log_error(str(game_season_month.season_id), "String not valid in: " + str(turnover))
                    else:
                        # Visiting team
                        if turnover.team_id == game.visitor_team_id:
                            visitor_team.make_turnover()
                            if turnover.player_id is not None:  # Main player
                                player_array = [player for player in visitor_players
                                                if (type(player).__name__ == "Player" and
                                                    turnover.player_id == player.id) or
                                                (type(player).__name__ == "PlayerHist" and
                                                 turnover.player_id == player.player_id)]
                                if len(player_array) == 1:
                                    player_array[0].make_turnover()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection main player in the play " + str(ele))
                            if turnover.steal_id is not None:  # Steal player
                                steal_array = [player for player in home_players
                                               if (type(player).__name__ == "Player" and turnover.steal_id == player.id)
                                               or
                                               (type(player).__name__ == "PlayerHist" and
                                                turnover.steal_id == player.player_id)]
                                if len(steal_array) == 1:
                                    home_team.make_steal()
                                    steal_array[0].make_steal()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection steal player in the play " + str(ele))

                        # Home team
                        elif turnover.team_id == game.home_team_id:
                            home_team.make_turnover()
                            if turnover.player_id is not None:  # Main player
                                player_array = [player for player in home_players
                                                if (type(player).__name__ == "Player" and
                                                    turnover.player_id == player.id) or
                                                (type(player).__name__ == "PlayerHist" and
                                                 turnover.player_id == player.player_id)]
                                if len(player_array) == 1:
                                    player_array[0].make_turnover()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection main player in the play " + str(ele))
                            if turnover.steal_id is not None:  # Steal player
                                steal_array = [player for player in visitor_players
                                               if (type(player).__name__ == "Player" and turnover.steal_id == player.id)
                                               or
                                               (type(player).__name__ == "PlayerHist" and
                                                turnover.steal_id == player.player_id)]
                                if len(steal_array) == 1:  # Steal player
                                    visitor_team.make_steal()
                                    steal_array[0].make_steal()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection steal player in the play " + str(ele))

                        PlayRepository.add_turnover(connection, turnover, turnover_count)  # Save play
                        turnover_count += 1

                # Foul
                elif "foul" in text:
                    foul = create_foul(play, ele, game.visitor_team_id, game.home_team_id, game_season_month.season_id)

                    if not foul.is_valid():
                        Log.log_error(str(game_season_month.season_id), "String not valid in: " + str(foul))
                    else:
                        # Visiting team
                        if foul.team_id == game.visitor_team_id:
                            visitor_team.make_foul()
                            if foul.player_id in no_played:
                                Log.log_info(str(game_season_month.season_id),
                                             "Foul made by a non-playing player: " + foul.player_id)
                            elif foul.player_id is not None:  # Main player
                                player_array = [player for player in visitor_players
                                                if (type(player).__name__ == "Player" and foul.player_id == player.id)
                                                or
                                                (type(player).__name__ == "PlayerHist" and
                                                 foul.player_id == player.player_id)]
                                if len(player_array) == 1:  # Main player
                                    player_array[0].make_foul()
                                elif foul.type == 'C':
                                    player_array = [player for player in home_players
                                                    if (type(player).__name__ == "Player" and
                                                        foul.player_id == player.id) or
                                                    (type(player).__name__ == "PlayerHist" and
                                                     foul.player_id == player.player_id)]
                                    if len(player_array) == 1:  # Main player
                                        visitor_team.remove_foul()
                                        foul.team_id = game.home_team_id
                                        home_team.make_foul()
                                        player_array[0].make_foul()
                                    else:
                                        Log.log_warning(str(game_season_month.season_id),
                                                        "Selection main player in the play " + str(ele))
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection main player in the play " + str(ele))
                            if foul.drawn_id is not None:  # Drawn player
                                drawn_array = [player for player in home_players
                                               if (type(player).__name__ == "Player" and foul.drawn_id == player.id) or
                                               (type(player).__name__ == "PlayerHist" and
                                                foul.drawn_id == player.player_id)
                                               ]
                                if len(drawn_array) == 1:  # Drawn player
                                    home_team.make_drawn()
                                    drawn_array[0].make_drawn()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection drawn player in the play " + str(ele))

                        # Home team
                        elif foul.team_id == game.home_team_id:
                            home_team.make_foul()
                            if foul.player_id in no_played:
                                Log.log_info(str(game_season_month.season_id),
                                             "Foul made by a non-playing player: " + foul.player_id)
                            elif foul.player_id is not None:  # Main player
                                player_array = [player for player in home_players
                                                if (type(player).__name__ == "Player" and foul.player_id == player.id)
                                                or
                                                (type(player).__name__ == "PlayerHist" and
                                                 foul.player_id == player.player_id)]
                                if len(player_array) == 1:  # Main player
                                    player_array[0].make_foul()
                                elif foul.type == 'C':
                                    player_array = [player for player in visitor_players
                                                    if (type(player).__name__ == "Player" and
                                                        foul.player_id == player.id)
                                                    or
                                                    (type(player).__name__ == "PlayerHist" and
                                                     foul.player_id == player.player_id)]
                                    if len(player_array) == 1:  # Main player
                                        home_team.remove_foul()
                                        foul.team_id = game.visitor_team_id
                                        visitor_team.make_foul()
                                        player_array[0].make_foul()
                                    else:
                                        Log.log_warning(str(game_season_month.season_id),
                                                        "Selection main player in the play " + str(ele))
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection main player in the play " + str(ele))
                            if foul.drawn_id is not None:  # Drawn player
                                drawn_array = [player for player in visitor_players
                                               if (type(player).__name__ == "Player" and foul.drawn_id == player.id) or
                                               (type(player).__name__ == "PlayerHist" and
                                                foul.drawn_id == player.player_id)
                                               ]
                                if len(drawn_array) == 1:  # Drawn player
                                    visitor_team.make_drawn()
                                    drawn_array[0].make_drawn()
                                else:
                                    Log.log_warning(str(game_season_month.season_id),
                                                    "Selection drawn player in the play " + str(ele))

                        PlayRepository.add_foul(connection, foul, foul_count)  # Save play
                        foul_count += 1

                # NOT WORKING because Not all changes appear in the web
                elif is_substitution_active and "enters the game for" in text:
                    substitution = create_substitution(play, ele, game_season_month.season_id)  # Create object

                    if not substitution.is_valid():
                        Log.log_error(str(game_season_month.season_id), "String not valid in: " + str(substitution))
                    else:
                        # Visiting team
                        if substitution.team_id == game.visitor_team_id:
                            enter_array = [player for player in visitor_players
                                           if (type(player).__name__ == "Player" and substitution.enter_id == player.id)
                                           or
                                           (type(player).__name__ == "PlayerHist" and
                                            substitution.enter_id == player.player_id)]
                            if len(enter_array) == 1:  # Main player
                                enter_array[0].enter_game(play.play_time, play.quarter)
                            else:
                                Log.log_error(str(game_season_month.season_id),
                                              "Selection enter player in the play " + str(ele))

                            leave_array = [player for player in visitor_players
                                           if (type(player).__name__ == "Player" and substitution.leave_id == player.id)
                                           or
                                           (type(player).__name__ == "PlayerHist" and
                                            substitution.leave_id == player.player_id)]
                            if len(leave_array) == 1:  # Main player
                                leave_array[0].leave_game(play.play_time, play.quarter)
                            else:
                                Log.log_error(str(game_season_month.season_id),
                                              "Selection leave player in the play " + str(ele))

                        # Home team
                        elif substitution.team_id == game.home_team_id:
                            enter_array = [player for player in home_players
                                           if (type(player).__name__ == "Player" and substitution.enter_id == player.id)
                                           or
                                           (type(player).__name__ == "PlayerHist" and
                                            substitution.enter_id == player.player_id)]
                            if len(enter_array) == 1:  # Main player
                                enter_array[0].enter_game(play.play_time, play.quarter)
                            else:
                                Log.log_error(str(game_season_month.season_id),
                                              "Selection enter player in the play " + str(ele))

                            leave_array = [player for player in home_players
                                           if (type(player).__name__ == "Player" and substitution.leave_id == player.id)
                                           or
                                           (type(player).__name__ == "PlayerHist" and
                                            substitution.leave_id == player.player_id)]
                            if len(leave_array) == 1:  # Main player
                                leave_array[0].leave_game(play.play_time, play.quarter)
                            else:
                                Log.log_error(str(game_season_month.season_id),
                                              "Selection leave player in the play " + str(ele))

                        PlayRepository.add_substitution(connection, substitution, substitution_count)  # Save play
                        substitution_count += 1
                else:
                    column += strings_ignored(ele, game_season_month.season_id, is_substitution_active)

            column += 1
            if column > 6:
                column = 1

        # Add to save the score in the Game, Teams and Players
        GameRepository.update_game_score_and_type(connection, game)

        # Save teams and players into database
        TeamService.update_team_score(connection, visitor_team, game_season_month.season_id)
        TeamService.update_team_score(connection, home_team, game_season_month.season_id)

        [PlayerService.update_player_score(connection, player, game_season_month.season_id)
         for player in visitor_players]
        [PlayerService.update_player_score(connection, player, game_season_month.season_id)
         for player in home_players]

        return game


def create_tree_or_two_points(play: Play, html: BeautifulSoup, points: int, season_id: int
                              ) -> ThreePointerPlay | TwoPointerPlay:
    """Create ThreePointerPlay or TwoPointerPlay object"""
    players = html.find_all('a')

    # Distance
    distance_exp = re.findall(r'from (\d\d?) ft', str(html))
    if len(distance_exp) > 0:
        distance = int(re.findall(r'from (\d\d?) ft', str(html))[0])
    else:
        distance = 0

    # Hit
    hit = is_scored(html, season_id)

    # Player
    player_id = players[0].get('href')[11:-5] if len(players) > 0 else None

    # Assist
    assist_id = None
    if "assist" in str(html):
        assist_id = players[1].get('href')[11:-5]
        if assist_id == "" or assist_id == "NULL":
            assist_id = None

    # Block
    block_id = None
    if "block" in str(html):
        block_id = players[1].get('href')[11:-5]
        if block_id == "" or block_id == "NULL":
            block_id = None

    # ThreePointer
    if points == 3:
        three_pointer = ThreePointerPlay().init_with_play(play, distance, hit, player_id, assist_id, block_id)
        return three_pointer

    # TwoPointer
    elif points == 2:
        two_pointer = TwoPointerPlay().init_with_play(play, distance, hit, player_id, assist_id, block_id)
        return two_pointer


def create_free_throw(play: Play, html: BeautifulSoup, season_id: int) -> FreeThrowPlay:
    """Create FreeThrowPlay object"""
    free_throw = FreeThrowPlay().init_with_play(play)

    # Hit
    free_throw.hit = is_scored(html, season_id)

    # Player
    free_throw.player_id = html.a.get('href')[11:-5] if html.a is not None else None

    return free_throw


def create_rebound(play: Play, html: BeautifulSoup, season_id: int) -> ReboundPlay:
    """Create ReboundPlay object"""
    rebound = ReboundPlay().init_with_play(play)

    # Type
    if "offensive" in str(html).lower():
        rebound.type = "O"
    elif "defensive" in str(html).lower():
        rebound.type = "D"
    else:
        Log.log_warning(str(season_id), "Rebound type not contemplated " + str(html))
        rebound.type = "X"

    # Player
    rebound.player_id = None
    if html.a is not None:
        player_id = html.a.get('href')[11:-5]
        if player_id is not None and player_id != "" and player_id != "NULL":
            rebound.player_id = player_id

    return rebound


def create_turnover(play: Play, html: BeautifulSoup, season_id: int) -> TurnoverPlay:
    """Create TurnoverPlay object"""
    turnover = TurnoverPlay().init_with_play(play)
    players = html.find_all('a')

    # Type
    if "turnover" in str(html).lower():
        turnover.type = "TO"
    elif "out of bounds lost ball" in str(html).lower():
        turnover.type = "OL"
    elif "lost ball" in str(html).lower():
        turnover.type = "LB"
    elif "bad pass" in str(html).lower():
        turnover.type = "BP"
    elif "traveling" in str(html).lower():
        turnover.type = "TR"
    elif "step out of bounds" in str(html).lower():
        turnover.type = "SB"
    elif "offensive foul" in str(html).lower():
        turnover.type = "OF"
    elif "shot clock" in str(html).lower():
        turnover.type = "SC"
    elif "palming" in str(html).lower():
        turnover.type = "PA"
    elif "dribble" in str(html).lower():
        turnover.type = "DB"
    elif "sec" in str(html).lower():
        turnover.type = "SE"
    elif "off goaltending" in str(html).lower():
        turnover.type = "OG"
    elif "back court" in str(html).lower():
        turnover.type = "BC"
    elif "inbound" in str(html).lower():
        turnover.type = "IB"
    elif "illegal assist" in str(html).lower():
        turnover.type = "IA"
    elif "lane violation" in str(html).lower():
        turnover.type = "LV"
    else:
        Log.log_warning(str(season_id), "Turnover type not contemplated " + str(html))
        turnover.type = "XX"

    # Players
    turnover.player_id = None
    turnover.steal_id = None
    if len(players) > 0:
        player_id = players[0].get('href')[11:-5]
        if player_id is not None and player_id != "" and player_id != "NULL":
            turnover.player_id = player_id
        # Steal
        if len(players) > 1:
            steal_id = players[1].get('href')[11:-5]
            if steal_id is not None and steal_id != "" and steal_id != "NULL":
                turnover.steal_id = steal_id

    return turnover


def create_foul(play: Play, html: BeautifulSoup, visitor_team: str, home_team: str, season_id: int) -> FoulPlay:
    """Create FoulPlay object"""
    foul = FoulPlay().init_with_play(play)
    players = html.find_all('a')

    # Type
    # In some types the team that make foul is the opposite
    if "shooting" in str(html).lower():  # Opposite team
        foul.type = "SH"
        if play.team_id == visitor_team:
            foul.team_id = home_team
        elif play.team_id == home_team:
            foul.team_id = visitor_team
    elif "loose ball" in str(html).lower():  # Normal team
        foul.type = "LB"
    elif "offensive charge" in str(html).lower():  # Normal team
        foul.type = "OC"
        if play.team_id == visitor_team:
            foul.team_id = home_team
        elif play.team_id == home_team:
            foul.team_id = visitor_team
    elif "offensive" in str(html).lower():  # Normal team
        foul.type = "OF"
    elif "technical" in str(html).lower() or "tech" in str(html).lower():  # Normal team
        foul.type = "TE"
    elif "away from play" in str(html).lower():  # Opposite team
        foul.type = "AF"
        if play.team_id == visitor_team:
            foul.team_id = home_team
        elif play.team_id == home_team:
            foul.team_id = visitor_team
    elif "personal" in str(html).lower():  # Opposite team
        foul.type = "PE"
        if play.team_id == visitor_team:
            foul.team_id = home_team
        elif play.team_id == home_team:
            foul.team_id = visitor_team
    elif "flagrant" in str(html).lower():  # Opposite team
        foul.type = "FL"
        if play.team_id == visitor_team:
            foul.team_id = home_team
        elif play.team_id == home_team:
            foul.team_id = visitor_team
    elif "clear path" in str(html).lower():  # Both
        foul.type = "CP"
    else:
        Log.log_warning(str(season_id), "Foul type not contemplated -> " + str(html))
        foul.type = "XX"

    # Player
    foul.player_id = None
    if len(players) > 0 and "coaches" not in players[0].get('href'):
        player_id = players[0].get('href')[11:-5]
        if player_id is not None and player_id != "" and player_id != "NULL":
            foul.player_id = player_id

    # Drawn
    foul.drawn_id = None
    if len(players) > 1:
        drawn_id = players[1].get('href')[11:-5]
        if drawn_id is not None and drawn_id != "" and drawn_id != "NULL":
            foul.drawn_id = drawn_id

    return foul


def create_substitution(play: Play, html: BeautifulSoup, season_id: int) -> SubstitutionPlay:
    """Create SubstitutionPlay object"""
    substitution = SubstitutionPlay().init_with_play(play)
    players = html.find_all('a')

    # Players
    substitution.enter_id = None
    substitution.leave_id = None
    if len(players) != 2:
        Log.log_error(str(season_id), "There are no two players in the substitution " + str(html))
    else:
        substitution.enter_id = players[0].get('href')[11:-5]
        substitution.leave_id = players[1].get('href')[11:-5]

    return substitution


def is_scored(text: BeautifulSoup, season_id) -> bool | None:
    """Set True when is makes
    and set False when is misses"""
    if "makes" in str(text):
        return True
    elif "misses" in str(text):
        return False
    else:
        Log.log_error(str(season_id), "Getting HIT -> " + str(text))
        return None


def strings_ignored(html: BeautifulSoup, season_id: int, is_substitution_active: bool) -> int:
    """Get other strings information in the table
    If string is jump ball, increment the column reader"""

    if not is_substitution_active and "enters the game for" in str(html).lower():
        column_increment = 0
    elif "timeout" in str(html).lower():
        column_increment = 0
    elif "violation" in str(html).lower():
        column_increment = 0
    elif "instant replay" in str(html).lower():
        column_increment = 0
    elif "ejected from game" in str(html).lower():
        column_increment = 0
    elif "jump ball" in str(html).lower():
        column_increment = 4
    elif "start of" in str(html).lower():
        column_increment = 4
    else:
        column_increment = 0
        Log.log_warning(str(season_id), "String not contemplated -> " + str(html))

    return column_increment


def delete_plays_from_season(connection: Connection, season_id: int):
    PlayRepository.delete_tree_points_from_season(connection, season_id)
    PlayRepository.delete_two_points_from_season(connection, season_id)
    PlayRepository.delete_free_throw_from_season(connection, season_id)
    PlayRepository.delete_rebound_from_season(connection, season_id)
    PlayRepository.delete_foul_from_season(connection, season_id)
    PlayRepository.delete_turnover_from_season(connection, season_id)
    PlayRepository.delete_substitution_from_season(connection, season_id)
