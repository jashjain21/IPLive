from typing import List, Optional, Dict, Any, Tuple
from dataclasses import asdict
import mysql.connector
import logging

from App.db_utils import get_db_manager
from App.models import Player, Match, BattingStat, BowlingStat
from App.constants import Table

logger = logging.getLogger(__name__)

try:
    from flask_caching import Cache
    cache_available = True
except ImportError:
    cache_available = False


@cache.memoize(timeout=600) if cache_available else lambda f: f
def get_all_matches() -> List[Match]:
    """Retrieve all completed matches from the database.

    Returns:
        List[Match]: A list of Match objects representing completed matches.
    """
    try:
        with get_db_manager() as conn:
            sql = f"SELECT * FROM {Table.MATCHH}"
            cursor = conn.cursor()
            cursor.execute(sql)
            match_rows = cursor.fetchall()
            matches = []
            for row in match_rows:
                if row[-1] and 'won' in str(row[-1]).split():
                    match = Match(
                        match_id=row[0],
                        team1=row[1],
                        team2=row[2],
                        stadium=row[3],
                        date=row[4],
                        result=row[-1]
                    )
                    matches.append(match)
        return matches[::-1]
    except mysql.connector.Error as e:
        logger.error("Database error in get_all_matches: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error in get_all_matches: %s", e)
        return []


def get_player_by_id(player_id: str) -> Optional[Player]:
    """Retrieve a player by their ID.

    Args:
        player_id (str): The unique identifier of the player.

    Returns:
        Optional[Player]: The Player object if found, None otherwise.
    """
    try:
        with get_db_manager() as conn:
            sql = f"SELECT * FROM {Table.PLAYER} WHERE PLAYER_ID = %s"
            cursor = conn.cursor()
            cursor.execute(sql, (player_id,))
            player_rows = cursor.fetchall()
            if not player_rows:
                logger.warning("No player found for ID %s", player_id)
                return None
            row = player_rows[0]
            player = Player(
                player_id=row[0],
                player_name=row[1],
                runs=row[2],
                balls_faced=row[3],
                wicket=row[4],
                runs_conceded=row[5],
                overs_bowled=row[6],
                matches_played=row[7],
                batting_strike_rate=row[8],
                economy=row[9],
                bowling_average=row[10],
                bowling_strike_rate=row[11],
                batting_average=row[12]
            )
        return player
    except mysql.connector.Error as e:
        logger.error("Database error in get_player_by_id for id %s: %s", player_id, e)
        return None
    except Exception as e:
        logger.error("Unexpected error in get_player_by_id for id %s: %s", player_id, e)
        return None


def search_players(name: str, team: str) -> List[Player]:
    """Search for players by name and team.

    Args:
        name (str): Partial or full name to search for.
        team (str): Team abbreviation to filter by.

    Returns:
        List[Player]: A list of Player objects matching the search criteria.
    """
    try:
        with get_db_manager() as conn:
            sql = f"SELECT * FROM {Table.PLAYER} WHERE PLAYER_NAME LIKE %s AND PLAYER_ID LIKE %s"
            cursor = conn.cursor()
            cursor.execute(sql, (f'%{name}%', f'%{team}%'))
            player_rows = cursor.fetchall()
            players = []
            for row in player_rows:
                player = Player(
                    player_id=row[0],
                    player_name=row[1],
                    runs=row[2],
                    balls_faced=row[3],
                    wicket=row[4],
                    runs_conceded=row[5],
                    overs_bowled=row[6],
                    matches_played=row[7],
                    batting_strike_rate=row[8],
                    economy=row[9],
                    bowling_average=row[10],
                    bowling_strike_rate=row[11],
                    batting_average=row[12]
                )
                players.append(player)
        return players
    except mysql.connector.Error as e:
        logger.error("Database error in search_players for name %s, team %s: %s", name, team, e)
        return []
    except Exception as e:
        logger.error("Unexpected error in search_players for name %s, team %s: %s", name, team, e)
        return []


def get_bowling_stats_by_match(match_id: str) -> List[Dict[str, Any]]:
    """Retrieve bowling statistics for a specific match.

    Args:
        match_id (str): The match ID.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing bowling stats.
    """
    try:
        with get_db_manager() as conn:
            sql = f"SELECT * FROM {Table.BOWLER} WHERE MATCH_ID = %s"
            cursor = conn.cursor()
            cursor.execute(sql, (match_id,))
            bowler_rows = cursor.fetchall()
            bowlers = []
            for row in bowler_rows:
                bowler = {}
                for i in range(len(row)):
                    if i == 0:
                        try:
                            name_sql = f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE PLAYER_ID = %s"
                            cursor.execute(name_sql, (row[i],))
                            name_result = cursor.fetchall()
                            bowler['name'] = name_result[0][0] if name_result else 'Unknown'
                        except (IndexError, mysql.connector.Error) as e:
                            logger.warning("Error fetching bowler name for ID %s in get_bowling_stats_by_match: %s", row[i], e)
                            bowler['name'] = 'Unknown'
                        bowler['team'] = row[i][:2:]
                    if i == 2:
                        bowler['wickets'] = row[i]
                    if i == 3:
                        bowler['economy'] = row[i]
                    if i == 6:
                        bowler['runs'] = row[i]
                    if i == 7:
                        bowler['overs'] = row[i]
                bowlers.append(bowler)
        return bowlers
    except mysql.connector.Error as e:
        logger.error("Database error in get_bowling_stats_by_match for match_id %s: %s", match_id, e)
        return []
    except Exception as e:
        logger.error("Unexpected error in get_bowling_stats_by_match for match_id %s: %s", match_id, e)
        return []


def get_batting_stats_by_match(match_id: str) -> List[Any]:
    """Retrieve batting statistics for a specific match.

    Args:
        match_id (str): The match ID.

    Returns:
        List[Any]: A complex list structure with team and player stats.
    """
    try:
        with get_db_manager() as conn:
            sql = f"SELECT * FROM {Table.BATSMAN} WHERE MATCH_ID = %s"
            sql2 = f"SELECT * FROM {Table.WICKETS} WHERE MATCH_ID = %s"
            sql3 = f"SELECT TEAM_1, TEAM_2 FROM {Table.MATCHH} WHERE MATCH_ID = %s"
            cursor = conn.cursor()
            cursor.execute(sql, (match_id,))
            batsman_rows = cursor.fetchall()
            cursor.execute(sql2, (match_id,))
            wicket_rows = cursor.fetchall()
            cursor.execute(sql3, (match_id,))
            team_rows = cursor.fetchall()
            
            if not team_rows:
                logger.warning("No teams found for match_id %s", match_id)
                return []
            
            t1 = team_rows[0][0]
            t2 = team_rows[0][1]
            prt = ""
            try:
                prt = batsman_rows[0][0][:2:]
            except IndexError:
                logger.warning("No batsman data for match_id %s", match_id)
            
            bat_list = []
            d = 0
            if len(batsman_rows) and t1[:2:] == batsman_rows[0][0][:2:]:
                bat_list.append(t1)
                bat_list.append([])
                d = 1
            else:
                bat_list.append(t2)
                bat_list.append([])
                d = 0
            
            for row in batsman_rows:
                if row[0][:2:] != prt:
                    bat_list.append(team_rows[0][d])
                    prt = row[0][:2:]
                    bat_list.append([])
                bat_dict = {}
                bat_dict['position'] = row[2]
                try:
                    name_sql = f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE PLAYER_ID = %s"
                    cursor.execute(name_sql, (row[0],))
                    name_result = cursor.fetchall()
                    bat_dict['name'] = name_result[0][0] if name_result else 'Unknown'
                except (IndexError, mysql.connector.Error) as e:
                    logger.warning("Error fetching batsman name for ID %s in get_batting_stats_by_match: %s", row[0], e)
                    bat_dict['name'] = 'Unknown'
                found = 1
                for w_row in wicket_rows:
                    if w_row[1] == row[0]:
                        found = 0
                        bat_dict['status'] = w_row[3]
                        break
                if found:
                    bat_dict['status'] = 'Not Out'
                bat_dict['fours'] = row[-2]
                bat_dict['sixes'] = row[-1]
                bat_dict['boundaries'] = row[-3]
                bat_dict['runs'] = row[3]
                bat_dict['balls'] = row[5]
                bat_dict['strike_rate'] = row[4]
                bat_list[-1].append(bat_dict)
            
            if len(bat_list) > 1:
                bat_list[1].sort(key=lambda x: int(x['position']))
            if len(bat_list) > 3:
                bat_list[-1].sort(key=lambda x: int(x['position']))
            
        return bat_list
    except mysql.connector.Error as e:
        logger.error("Database error in get_batting_stats_by_match for match_id %s: %s", match_id, e)
        return []
    except Exception as e:
        logger.error("Unexpected error in get_batting_stats_by_match for match_id %s: %s", match_id, e)
        return []


def get_wickets_by_match(match_id: str) -> List[Any]:
    """Retrieve wickets data for a specific match.

    Args:
        match_id (str): The match ID.

    Returns:
        List[Any]: A complex list structure with wickets information.
    """
    try:
        with get_db_manager() as conn:
            sql2 = f"SELECT * FROM {Table.WICKETS} WHERE MATCH_ID = %s"
            cursor = conn.cursor()
            cursor.execute(sql2, (match_id,))
            wicket_rows = cursor.fetchall()
            sql3 = f"SELECT TEAM_1, TEAM_2 FROM {Table.MATCHH} WHERE MATCH_ID = %s"
            cursor.execute(sql3, (match_id,))
            team_rows = cursor.fetchall()
            
            if not team_rows:
                logger.warning("No teams found for match_id %s", match_id)
                return []
            
            t1 = team_rows[0][0]
            t2 = team_rows[0][1]
            prt = ""
            try:
                prt = wicket_rows[0][1][:2:]
            except IndexError:
                logger.warning("No wickets data for match_id %s", match_id)
            
            d = 0
            wick_list = []
            if len(wicket_rows) and t1[:2:] == wicket_rows[0][0][:2:]:
                wick_list.append(t1)
                wick_list.append([])
                d = 1
            else:
                wick_list.append(t2)
                wick_list.append([])
                d = 0
            
            for row in wicket_rows:
                if row[1][:2:] != prt:
                    wick_list.append(team_rows[0][d])
                    prt = row[1][:2:]
                    wick_list.append([])
                wick_dict = {}
                wick_dict['over'] = row[-1]
                try:
                    name_sql = f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE PLAYER_ID = %s"
                    cursor.execute(name_sql, (row[1],))
                    name_result = cursor.fetchall()
                    wick_dict['name'] = name_result[0][0] if name_result else 'Unknown'
                except (IndexError, mysql.connector.Error) as e:
                    logger.warning("Error fetching wicket player name for ID %s in get_wickets_by_match: %s", row[1], e)
                    wick_dict['name'] = 'Unknown'
                try:
                    score_sql = f"SELECT RUNS FROM {Table.SCORE} WHERE OVER_BALL = %s AND MATCH_ID = %s AND TEAM = %s"
                    cursor.execute(score_sql, (row[-1], match_id, wick_list[-2]))
                    score_result = cursor.fetchall()
                    wick_dict['score'] = score_result[0][0] if score_result else ""
                except (IndexError, mysql.connector.Error) as e:
                    logger.warning("Error fetching score for over %s in get_wickets_by_match: %s", row[-1], e)
                    wick_dict['score'] = ""
                wick_dict['wickets'] = row[2]
                wick_list[-1].append(wick_dict)
            
            if len(wick_list) > 1:
                wick_list[1].sort(key=lambda x: x['wickets'])
            if len(wick_list) > 3:
                wick_list[-1].sort(key=lambda x: x['wickets'])
            
        return wick_list
    except mysql.connector.Error as e:
        logger.error("Database error in get_wickets_by_match for match_id %s: %s", match_id, e)
        return []
    except Exception as e:
        logger.error("Unexpected error in get_wickets_by_match for match_id %s: %s", match_id, e)
        return []


def get_score_summaries_by_match(match_id: str, team1: str, team2: str) -> Dict[str, List[Dict[str, Any]]]:
    """Retrieve score summaries for both teams in a match.

    Args:
        match_id (str): The match ID.
        team1 (str): The first team.
        team2 (str): The second team.

    Returns:
        Dict[str, List[Dict[str, Any]]]: Dictionary with team scores.
    """
    try:
        with get_db_manager() as conn:
            sql = f"SELECT * FROM {Table.SCORE} WHERE MATCH_ID = %s AND TEAM = %s"
            cursor = conn.cursor()
            cursor.execute(sql, (match_id, team1))
            scores1 = cursor.fetchall()
            cursor.execute(sql, (match_id, team2))
            scores2 = cursor.fetchall()
            scores1.sort(key=lambda x: float(x[0]))
            scores2.sort(key=lambda x: float(x[0]))
            
            for score in scores1:
                score_list = list(score)
                try:
                    name_sql = f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE PLAYER_ID = %s"
                    cursor.execute(name_sql, (score_list[2],))
                    result = cursor.fetchall()
                    score_list[2] = result[0][0] if result else 'Unknown'
                except (IndexError, mysql.connector.Error) as e:
                    logger.warning("Error fetching batsman1 name for score in get_score_summaries_by_match: %s", e)
                    score_list[2] = 'Unknown'
                try:
                    cursor.execute(name_sql, (score_list[3],))
                    result = cursor.fetchall()
                    score_list[3] = result[0][0] if result else 'Unknown'
                except (IndexError, mysql.connector.Error) as e:
                    logger.warning("Error fetching batsman2 name for score in get_score_summaries_by_match: %s", e)
                    score_list[3] = 'Unknown'
                try:
                    cursor.execute(name_sql, (score_list[4],))
                    result = cursor.fetchall()
                    score_list[4] = result[0][0] if result else 'Unknown'
                except (IndexError, mysql.connector.Error) as e:
                    logger.warning("Error fetching bowler name for score in get_score_summaries_by_match: %s", e)
                    score_list[4] = 'Unknown'
            
            for score in scores2:
                score_list = list(score)
                try:
                    name_sql = f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE PLAYER_ID = %s"
                    cursor.execute(name_sql, (score_list[2],))
                    result = cursor.fetchall()
                    score_list[2] = result[0][0] if result else 'Unknown'
                except (IndexError, mysql.connector.Error) as e:
                    logger.warning("Error fetching batsman1 name for score in get_score_summaries_by_match: %s", e)
                    score_list[2] = 'Unknown'
                try:
                    cursor.execute(name_sql, (score_list[3],))
                    result = cursor.fetchall()
                    score_list[3] = result[0][0] if result else 'Unknown'
                except (IndexError, mysql.connector.Error) as e:
                    logger.warning("Error fetching batsman2 name for score in get_score_summaries_by_match: %s", e)
                    score_list[3] = 'Unknown'
                try:
                    cursor.execute(name_sql, (score_list[4],))
                    result = cursor.fetchall()
                    score_list[4] = result[0][0] if result else 'Unknown'
                except (IndexError, mysql.connector.Error) as e:
                    logger.warning("Error fetching bowler name for score in get_score_summaries_by_match: %s", e)
                    score_list[4] = 'Unknown'
            
        scores = {team1: scores1, team2: scores2}
        return scores
    except mysql.connector.Error as e:
        logger.error("Database error in get_score_summaries_by_match for match_id %s, teams %s, %s: %s", match_id, team1, team2, e)
        return {}
    except Exception as e:
        logger.error("Unexpected error in get_score_summaries_by_match for match_id %s, teams %s, %s: %s", match_id, team1, team2, e)
        return {}


def get_score_by_over(match_id: str, team: str, over: str) -> List[Any]:
    """Retrieve score for a specific over in a match.

    Args:
        match_id (str): The match ID.
        team (str): The team.
        over (str): The over number.

    Returns:
        List[Any]: The score data for the over.
    """
    try:
        with get_db_manager() as conn:
            sql = f"SELECT * FROM {Table.SCORE} WHERE MATCH_ID = %s AND TEAM = %s AND OVER_BALL = %s"
            cursor = conn.cursor()
            cursor.execute(sql, (match_id, team, over))
            scores = cursor.fetchall()
            if not scores:
                logger.warning("No score found for match_id %s, team %s, over %s", match_id, team, over)
                return []
            score = list(scores[0])
            
            try:
                name_sql = f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE PLAYER_ID = %s"
                cursor.execute(name_sql, (score[2],))
                result = cursor.fetchall()
                score[2] = result[0][0] if result else 'Unknown'
            except (IndexError, mysql.connector.Error) as e:
                logger.warning("Error fetching batsman1 name in get_score_by_over: %s", e)
                score[2] = 'Unknown'
            try:
                cursor.execute(name_sql, (score[3],))
                result = cursor.fetchall()
                score[3] = result[0][0] if result else 'Unknown'
            except (IndexError, mysql.connector.Error) as e:
                logger.warning("Error fetching batsman2 name in get_score_by_over: %s", e)
                score[3] = 'Unknown'
            try:
                cursor.execute(name_sql, (score[4],))
                result = cursor.fetchall()
                score[4] = result[0][0] if result else 'Unknown'
            except (IndexError, mysql.connector.Error) as e:
                logger.warning("Error fetching bowler name in get_score_by_over: %s", e)
                score[4] = 'Unknown'
        return score
    except mysql.connector.Error as e:
        logger.error("Database error in get_score_by_over for match_id %s, team %s, over %s: %s", match_id, team, over, e)
        return []
    except Exception as e:
        logger.error("Unexpected error in get_score_by_over for match_id %s, team %s, over %s: %s", match_id, team, over, e)
        return []


def get_team_names_by_match_id(match_id: str) -> Tuple[str, str]:
    """Retrieve team names for a match.

    Args:
        match_id (str): The match ID.

    Returns:
        Tuple[str, str]: The names of team1 and team2.
    """
    try:
        with get_db_manager() as conn:
            cursor = conn.cursor()
            sql3 = f"SELECT TEAM_1, TEAM_2 FROM {Table.MATCHH} WHERE MATCH_ID = %s"
            cursor.execute(sql3, (match_id,))
            teams = cursor.fetchall()
            if not teams:
                logger.warning("No teams found for match_id %s", match_id)
                return '', ''
            t1 = teams[0][0]
            t2 = teams[0][1]
        return t1, t2
    except mysql.connector.Error as e:
        logger.error("Database error in get_team_names_by_match_id for id %s: %s", match_id, e)
        return '', ''
    except Exception as e:
        logger.error("Unexpected error in get_team_names_by_match_id for id %s: %s", match_id, e)
        return '', ''


def get_top_players_stats() -> Dict[str, str]:
    """Retrieve top players statistics.

    Returns:
        Dict[str, str]: Dictionary with top player names for various categories.
    """
    try:
        with get_db_manager() as conn:
            cursor = conn.cursor()
            stats = {}
            
            # Orange cap (most runs)
            try:
                cursor.execute(f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE RUNS = (SELECT MAX(RUNS) FROM {Table.PLAYER} WHERE RUNS > 0)")
                result = cursor.fetchall()
                stats['orange_cap'] = result[0][0] if result else ""
            except mysql.connector.Error as e:
                logger.warning("Error fetching orange cap: %s", e)
                stats['orange_cap'] = ""
            
            # Purple cap (most wickets)
            try:
                cursor.execute(f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE WICKET = (SELECT MAX(WICKET) FROM {Table.PLAYER} WHERE WICKET > 0)")
                result = cursor.fetchall()
                stats['purple_cap'] = result[0][0] if result else ""
            except mysql.connector.Error as e:
                logger.warning("Error fetching purple cap: %s", e)
                stats['purple_cap'] = ""
            
            # Best economy
            try:
                cursor.execute(f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE ECONOMY = (SELECT MIN(ECONOMY) FROM {Table.PLAYER} WHERE ECONOMY > 0)")
                result = cursor.fetchall()
                stats['best_economy'] = result[0][0] if result else ""
            except mysql.connector.Error as e:
                logger.warning("Error fetching best economy: %s", e)
                stats['best_economy'] = ""
            
            # Best strike rate (batting)
            try:
                cursor.execute(f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE BATTING_STRIKE_RATE = (SELECT MAX(BATTING_STRIKE_RATE) FROM {Table.PLAYER} WHERE BATTING_STRIKE_RATE > 0)")
                result = cursor.fetchall()
                stats['best_strike_rate'] = result[0][0] if result else ""
            except mysql.connector.Error as e:
                logger.warning("Error fetching best strike rate: %s", e)
                stats['best_strike_rate'] = ""
            
            # Best bowling strike rate
            try:
                cursor.execute(f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE BOWLING_STRIKE_RATE = (SELECT MIN(BOWLING_STRIKE_RATE) FROM {Table.PLAYER} WHERE BOWLING_STRIKE_RATE > 0)")
                result = cursor.fetchall()
                stats['bowling_strike_rate'] = result[0][0] if result else ""
            except mysql.connector.Error as e:
                logger.warning("Error fetching bowling strike rate: %s", e)
                stats['bowling_strike_rate'] = ""
            
            # Best bowling average
            try:
                cursor.execute(f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE BOWLING_AVERAGE = (SELECT MIN(BOWLING_AVERAGE) FROM {Table.PLAYER} WHERE BOWLING_AVERAGE > 0)")
                result = cursor.fetchall()
                stats['bowling_average'] = result[0][0] if result else ""
            except mysql.connector.Error as e:
                logger.warning("Error fetching bowling average: %s", e)
                stats['bowling_average'] = ""
            
            # Best batting average
            try:
                cursor.execute(f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE BATTING_AVERAGE = (SELECT MAX(BATTING_AVERAGE) FROM {Table.PLAYER} WHERE BATTING_AVERAGE > 0)")
                result = cursor.fetchall()
                stats['batting_average'] = result[0][0] if result else ""
            except mysql.connector.Error as e:
                logger.warning("Error fetching batting average: %s", e)
                stats['batting_average'] = ""
        
        return stats
    except Exception as e:
        logger.error("Unexpected error in get_top_players_stats: %s", e)
        return {'orange_cap': '', 'purple_cap': '', 'best_economy': '', 'best_strike_rate': '', 'bowling_strike_rate': '', 'bowling_average': '', 'batting_average': ''}


def get_final_score_summary(match_id: str, team1: str, team2: str) -> Dict[str, Any]:
    """Retrieve final score summary for a match.

    Args:
        match_id (str): The match ID.
        team1 (str): The first team.
        team2 (str): The second team.

    Returns:
        Dict[str, Any]: Dictionary with inning details.
    """
    try:
        with get_db_manager() as conn:
            cursor = conn.cursor()
            final_score = {'inning1': {}, 'inning2': {}}
            
            cursor.execute(f"SELECT * FROM {Table.SCORE} WHERE MATCH_ID = %s AND RRR IS NULL", (match_id,))
            data = cursor.fetchall()
            if not data:
                logger.warning("No score data for match_id %s", match_id)
                return final_score
            
            lst_ball = max(data, key=lambda x: float(x[0]))[0]
            cursor.execute(
                f"SELECT RUNS, WICKET, TEAM FROM {Table.SCORE} WHERE MATCH_ID = %s AND OVER_BALL = %s AND RRR IS NULL",
                (match_id, str(lst_ball))
            )
            inn1_data = cursor.fetchall()
            if not inn1_data:
                logger.warning("No inning1 data for match_id %s", match_id)
                return final_score
            
            final_score['inning1']['runs'] = inn1_data[0][0]
            final_score['inning1']['wicket'] = inn1_data[0][1]
            final_score['inning1']['team'] = inn1_data[0][2]
            final_score['inning1']['over_ball'] = lst_ball

            cursor.execute(f"SELECT * FROM {Table.SCORE} WHERE MATCH_ID = %s AND TEAM != %s", (match_id, inn1_data[0][2]))
            data = cursor.fetchall()
            if not data:
                logger.warning("No inning2 data for match_id %s", match_id)
                return final_score
            
            lst_ball = max(data, key=lambda x: float(x[0]))[0]
            cursor.execute(
                f"SELECT * FROM {Table.SCORE} WHERE MATCH_ID = %s AND OVER_BALL = %s AND TEAM <> %s",
                (match_id, lst_ball, inn1_data[0][2])
            )
            inn2_data = cursor.fetchall()
            if not inn2_data:
                logger.warning("No detailed inning2 data for match_id %s", match_id)
                return final_score
            
            final_score['inning2']['team'] = inn2_data[0][5]
            final_score['inning2']['runs'] = inn2_data[0][6]
            final_score['inning2']['wickets'] = inn2_data[0][7]
            final_score['inning2']['over_ball'] = inn2_data[0][0]

            try:
                cursor.execute(f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE PLAYER_ID = %s", (inn2_data[0][2],))
                result = cursor.fetchall()
                final_score['inning2']['bat1'] = result[0][0] if result else 'Unknown'
            except (IndexError, mysql.connector.Error) as e:
                logger.warning("Error fetching bat1 name in get_final_score_summary: %s", e)
                final_score['inning2']['bat1'] = 'Unknown'

            try:
                cursor.execute(f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE PLAYER_ID = %s", (inn2_data[0][3],))
                result = cursor.fetchall()
                final_score['inning2']['bat2'] = result[0][0] if result else 'Unknown'
            except (IndexError, mysql.connector.Error) as e:
                logger.warning("Error fetching bat2 name in get_final_score_summary: %s", e)
                final_score['inning2']['bat2'] = 'Unknown'

            try:
                cursor.execute(f"SELECT PLAYER_NAME FROM {Table.PLAYER} WHERE PLAYER_ID = %s", (inn2_data[0][4],))
                result = cursor.fetchall()
                final_score['inning2']['bowl'] = result[0][0] if result else 'Unknown'
            except (IndexError, mysql.connector.Error) as e:
                logger.warning("Error fetching bowl name in get_final_score_summary: %s", e)
                final_score['inning2']['bowl'] = 'Unknown'

            try:
                cursor.execute(f"SELECT * FROM {Table.BATSMAN} WHERE MATCH_ID = %s AND PLAYER_ID = %s", (match_id, inn2_data[0][2]))
                bat1 = cursor.fetchall()
                final_score['inning2']['run1'] = bat1[0][3] if bat1 else 0
                final_score['inning2']['balls_faced_1'] = bat1[0][5] if bat1 else 0
            except (IndexError, mysql.connector.Error) as e:
                logger.warning("Error fetching bat1 stats in get_final_score_summary: %s", e)
                final_score['inning2']['run1'] = 0
                final_score['inning2']['balls_faced_1'] = 0

            try:
                cursor.execute(f"SELECT * FROM {Table.BATSMAN} WHERE MATCH_ID = %s AND PLAYER_ID = %s", (match_id, inn2_data[0][3]))
                bat2 = cursor.fetchall()
                final_score['inning2']['run2'] = bat2[0][3] if bat2 else 0
                final_score['inning2']['balls_faced_2'] = bat2[0][5] if bat2 else 0
            except (IndexError, mysql.connector.Error) as e:
                logger.warning("Error fetching bat2 stats in get_final_score_summary: %s", e)
                final_score['inning2']['run2'] = 0
                final_score['inning2']['balls_faced_2'] = 0

            try:
                cursor.execute(f"SELECT * FROM {Table.BOWLER} WHERE MATCH_ID = %s AND PLAYER_ID = %s", (match_id, inn2_data[0][4]))
                bowl = cursor.fetchall()
                if bowl:
                    final_score['inning2']['bowl_wick'] = bowl[0][2]
                    final_score['inning2']['balls_run'] = bowl[0][6]
                else:
                    final_score['inning2']['bowl_wick'] = 0
                    final_score['inning2']['balls_run'] = 0
            except (IndexError, mysql.connector.Error) as e:
                logger.warning("Error fetching bowl stats in get_final_score_summary: %s", e)
                final_score['inning2']['bowl_wick'] = 0
                final_score['inning2']['balls_run'] = 0
            
            overs = final_score['inning2']['over_ball']
            try:
                over = int(float(overs))
                if float(overs) != int(float(overs)):
                    ball = float(overs) - int(float(overs))
                    ball /= 0.6
                    over += ball
                final_score['inning2']['crr'] = round(final_score['inning2']['runs'] / over, 2) if over > 0 else 0
            except (ValueError, ZeroDivisionError) as e:
                logger.warning("Error calculating CRR in get_final_score_summary: %s", e)
                final_score['inning2']['crr'] = 0
        
        return final_score
    except mysql.connector.Error as e:
        logger.error("Database error in get_final_score_summary for match_id %s: %s", match_id, e)
        return {'inning1': {}, 'inning2': {}}
    except Exception as e:
        logger.error("Unexpected error in get_final_score_summary for match_id %s: %s", match_id, e)
        return {'inning1': {}, 'inning2': {}}