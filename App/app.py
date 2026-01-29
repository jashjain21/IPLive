from flask import Flask, g, current_app, render_template, request, redirect
import mysql.connector
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use MockCricbuzz for offline mode (no external API calls)
from App.mock_data import MockCricbuzz, mock_live_score
from App.databases import DatabaseManager
from App.db_utils import get_db_manager
from App.constants import Team, TEAM_MAPPING, ALL_TEAMS, Table
from App.models import Player, Match, BattingStat, BowlingStat
from App.repository import (
    get_all_matches,
    get_player_by_id,
    search_players,
    get_bowling_stats_by_match,
    get_batting_stats_by_match,
    get_wickets_by_match,
    get_score_summaries_by_match,
    get_score_by_over,
    get_team_names_by_match_id,
    get_top_players_stats,
    get_final_score_summary
)
try:
    from flask_caching import Cache
except ImportError:
    Cache = None

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'database': os.environ.get('DB_NAME', 'scratch')
}

# Flask app
app = Flask(__name__)
app.config['DB_CONFIG'] = DB_CONFIG
# Cache configuration
if Cache:
    cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})  # 5 minutes
else:
    cache = None



def teamname(s):
    """Convert full team name to abbreviation."""
    return TEAM_MAPPING.get(s, s)


def prv_inn(sc):
    """Get previous innings data."""
    if len(sc['scorecard']) > 1:
        over_ball = sc['scorecard'][1]['overs']
        over = int(float(over_ball))
        if float(over_ball) != int(float(over_ball)):
            ball = float(over_ball) - int(float(over_ball))
            ball /= 0.6
            over += ball
        crr = 0
        if over != 0:
            crr = int(sc['scorecard'][0]['runs']) / over
        
        return {
            'runs': sc['scorecard'][1]['runs'],
            'wickets': sc['scorecard'][1]['wickets'],
            'crr': crr,
            'team': teamname(sc['scorecard'][1]['batteam']),
            'over_ball': sc['scorecard'][1]['overs']
        }
    else:
        return {
            'runs': '-',
            'wickets': '-',
            'crr': '-',
            'team': teamname(sc['scorecard'][0]['bowlteam']),
            'over_ball': '-'
        }



def do_it():
    """
    Get current match data from mock/database.
    In offline mode, this returns mock match ID and uses pre-seeded data.
    """
    c = MockCricbuzz()
    # Get matches from mock data
    matches = c.matches()
    if matches:
        match_id = matches[0]['id']
        # Use mock live score data
        live_score = mock_live_score.copy()
        return match_id, live_score
    return 'M001', mock_live_score.copy()  # Default match ID


def index():
    """Home page with live/mock score."""
    logger.info("Request to / (index)")
    try:
        matchid, ls = do_it()
        c = MockCricbuzz()
        sc = c.scorecard(matchid)
        pr_in = {}
        bowl_tbl = []
        bat_t = []
        w_t = []
        
        if sc.get('scorecard') and len(sc['scorecard']) > 0:
            pr_in = prv_inn(sc)
            bowl_tbl = get_bowling_stats_by_match(matchid)
            bat_t = get_batting_stats_by_match(matchid)
            w_t = get_wickets_by_match(matchid)
        
        return render_template('index.html', ls=ls, prin=pr_in, bt=bowl_tbl, batt=bat_t, wt=w_t)
    except Exception as e:
        logger.error("Error in index: %s", e)
        return render_template('index.html', ls=mock_live_score.copy(), prin={}, bt=[], batt=[], wt=[]), 500


@app.route('/archive/')
def archive():
    """Archive page with list of matches."""
    logger.info("Request to /archive/")
    try:
        m_tb = get_all_matches()
        return render_template('archive.html', mtb=m_tb)
    except Exception as e:
        logger.error("Error in archive: %s", e)
        return render_template('archive.html', mtb=[]), 500


@app.route('/archive/match')
def matchc():
    """Single match details."""
    id = request.args.get('id', default="", type=str)
    logger.info("Request to /archive/match with id %s", id)
    try:
        bat_t = get_batting_stats_by_match(id)
        bowl_tbl = get_bowling_stats_by_match(id)
        w_t = get_wickets_by_match(id)
        f_s = {}
        if len(bat_t) >= 3:
            f_s = get_final_score_summary(id, bat_t[0], bat_t[2])
        return render_template('match.html', batt=bat_t, bt=bowl_tbl, wt=w_t, fs=f_s)
    except Exception as e:
        logger.error("Error in matchc for id %s: %s", id, e)
        return render_template('match.html', batt=[], bt=[], wt=[], fs={}), 500


@app.route('/playerstats/', methods=['GET', 'POST'])
def player():
    """Player statistics page."""
    logger.info("Request to /playerstats/")
    teams = ALL_TEAMS
    plyrs = search_players("", "")
    
    try:
        # Get stats from database (replaces IPLive class methods)
        stats = get_top_players_stats()
        o_c = stats.get('orange_cap', '')
        p_c = stats.get('purple_cap', '')
        b_e = stats.get('best_economy', '')
        s_r = stats.get('best_strike_rate', '')
        b_sr = stats.get('bowling_strike_rate', '')
        b_a = stats.get('bowling_average', '')
        a = stats.get('batting_average', '')
    except Exception as e:
        logger.error("Error getting player stats: %s", e)
        o_c = p_c = b_e = s_r = b_sr = b_a = a = ''
    
    if request.method == 'POST':
        try:
            plname = request.form['plyr']
            plteam = request.form['team']
            logger.info("POST to /playerstats/ with name %s, team %s", plname, plteam)
            plyrs = search_players(plname, plteam)
        except KeyError as e:
            logger.warning("Missing form data in player: %s", e)
            plyrs = search_players("", "")
        except Exception as e:
            logger.error("Error in POST player: %s", e)
            plyrs = search_players("", "")
    
    return render_template('playerstat.html', pls=plyrs, ts=teams, oc=o_c, pc=p_c, be=b_e, sr=s_r, bsr=b_sr, bav=b_a, av=a)


@app.route('/playerstats/player')
def playerst():
    """Individual player page."""
    id = request.args.get('id', default="", type=str)
    logger.info("Request to /playerstats/player with id %s", id)
    try:
        pl_r = get_player_by_id(id)
        teams = ALL_TEAMS
        return render_template('player.html', player=pl_r, ts=teams)
    except Exception as e:
        logger.error("Error in playerst for id %s: %s", id, e)
        return render_template('player.html', player=None, ts=ALL_TEAMS), 500


@app.route('/archive/score', methods=['GET', 'POST'])
def score_bb():
    """Ball-by-ball score page."""
    id = request.args.get('id', default="", type=str)
    logger.info("Request to /archive/score with id %s", id)
    try:
        team1, team2 = get_team_names_by_match_id(id)
        scrs = get_score_summaries_by_match(id, team1, team2)
    except Exception as e:
        logger.error("Error in score_bb for id %s: %s", id, e)
        return render_template('score.html', scores={}, score=[], match=id), 500
    
    if request.method == 'POST':
        try:
            scrover = request.form['over']
            scrteam = request.form['team']
            logger.info("POST to /archive/score with over %s, team %s", scrover, scrteam)
            scr = get_score_by_over(id, scrteam, scrover)
            return render_template('score.html', scores=scrs, score=scr, match=id)
        except KeyError as e:
            logger.warning("Missing form data in score_bb: %s", e)
            return render_template('score.html', scores=scrs, score=[], match=id), 400
        except Exception as e:
            logger.error("Error in POST score_bb: %s", e)
            return render_template('score.html', scores=scrs, score=[], match=id), 500
    else:
        return render_template('score.html', scores=scrs, score=[], match=id)


@app.errorhandler(404)
def not_found(error):
    logger.error("404 error: %s", error)
    return "Page not found", 404


@app.errorhandler(500)
def internal_error(error):
    logger.error("500 error: %s", error)
    return "Internal server error", 500


if __name__ == "__main__":
    app.run(debug=True)
