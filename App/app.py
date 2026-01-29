from flask import Flask, render_template, request, redirect
import mysql.connector
import os

# Use MockCricbuzz for offline mode (no external API calls)
from mock_data import MockCricbuzz, mock_live_score

# Initialize mock cricbuzz (replaces pycricbuzz.Cricbuzz)
c = MockCricbuzz()

global_pr = {}
live_score = mock_live_score.copy()

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'database': os.environ.get('DB_NAME', 'scratch')
}

myconn = mysql.connector.connect(**DB_CONFIG)

# Team name mapping
TEAM_MAPPING = {
    "Chennai Super Kings": "CSK",
    "Mumbai Indians": "MI",
    "Royal Challengers Bangalore": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Sunrisers Hyderabad": "SRH",
    "Kings XI Punjab": "KXIP",
    "Delhi Capitals": "DC",
    "Rajasthan Royals": "RR"
}

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


def db_to_bowl(match_id):
    """Get bowling data from database."""
    sql = "SELECT * FROM BOWLER WHERE MATCH_ID = %s"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql, (match_id,))
    bowtable = iplcursor.fetchall()
    table = []
    for j in bowtable:
        row = {}
        for i in range(len(j)):
            if i == 0:
                a = "SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID = %s"
                iplcursor.execute(a, (j[i],))
                name = iplcursor.fetchall()
                row['name'] = name[0][0]
                row['team'] = j[i][:2:]
            if i == 2:
                row['wicks'] = j[i]
            if i == 3:
                row['econ'] = j[i]
            if i == 6:
                row['runs'] = j[i]
            if i == 7:
                row['over'] = j[i]
        table.append(row)
    return table


def db_to_match():
    """Get all matches from database."""
    sql = "SELECT * FROM MATCHH"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql)
    matchtable = iplcursor.fetchall()
    matchtb = []
    for i in matchtable:
        if i[-1] and 'won' in str(i[-1]).split():
            match = {
                'id': i[0],
                'team1': i[1],
                'team2': i[2],
                'stad': i[3],
                'date': i[4],
                'result': i[-1]
            }
            matchtb.append(match)
    return matchtb[::-1]


def do_it():
    """
    Get current match data from mock/database.
    In offline mode, this returns mock match ID and uses pre-seeded data.
    """
    global live_score
    
    # Get matches from mock data
    matches = c.matches()
    if matches:
        match_id = matches[0]['id']
        # Use mock live score data
        live_score = mock_live_score.copy()
        return match_id
    return 'M001'  # Default match ID


def db_to_bat(match_id):
    """Get batting data from database."""
    sql = "SELECT * FROM BATSMAN WHERE MATCH_ID = %s"
    sql2 = "SELECT * FROM WICKETS WHERE MATCH_ID = %s"
    sql3 = "SELECT TEAM_1, TEAM_2 FROM MATCHH WHERE MATCH_ID = %s"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql, (match_id,))
    battable = iplcursor.fetchall()
    iplcursor.execute(sql2, (match_id,))
    wittable = iplcursor.fetchall()
    iplcursor.execute(sql3, (match_id,))
    teams = iplcursor.fetchall()
    
    if not teams:
        return []
    
    t1 = teams[0][0]
    t2 = teams[0][1]
    prt = ""
    try:
        prt = battable[0][0][:2:]
    except:
        pass
    
    bat_tb = []
    d = 0
    if len(battable) and t1[:2:] == battable[0][0][:2:]:
        bat_tb.append(t1)
        bat_tb.append([])
        d = 1
    else:
        bat_tb.append(t2)
        bat_tb.append([])
        d = 0
    
    for i in battable:
        if i[0][:2:] != prt:
            bat_tb.append(teams[0][d])
            prt = i[0][:2:]
            bat_tb.append([])
        bat_i = {}
        bat_i['pos'] = i[2]
        a = "SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID = %s"
        iplcursor.execute(a, (i[0],))
        name = iplcursor.fetchall()
        found = 1
        bat_i['name'] = name[0][0]
        for j in wittable:
            if j[1] == i[0]:
                found = 0
                bat_i['stat'] = j[3]
                break
        if found:
            bat_i['stat'] = 'Not Out'
        bat_i['4s'] = i[-2]
        bat_i['6s'] = i[-1]
        bat_i['bounds'] = i[-3]
        bat_i['runs'] = i[3]
        bat_i['ball'] = i[5]
        bat_i['sr'] = i[4]
        bat_tb[-1].append(bat_i)
    
    if len(bat_tb) > 1:
        bat_tb[1].sort(key=lambda i: int(i['pos']))
    if len(bat_tb) > 3:
        bat_tb[-1].sort(key=lambda i: int(i['pos']))
    
    return bat_tb


def db_to_wick(match_id):
    """Get wickets data from database."""
    sql2 = "SELECT * FROM WICKETS WHERE MATCH_ID = %s"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql2, (match_id,))
    wittable = iplcursor.fetchall()
    sql3 = "SELECT TEAM_1, TEAM_2 FROM MATCHH WHERE MATCH_ID = %s"
    iplcursor.execute(sql3, (match_id,))
    teams = iplcursor.fetchall()
    
    if not teams:
        return []
    
    t1 = teams[0][0]
    t2 = teams[0][1]
    prt = ""
    try:
        prt = wittable[0][1][:2:]
    except:
        pass
    
    d = 0
    wick = []
    if len(wittable) and t1[:2:] == wittable[0][0][:2:]:
        wick.append(t1)
        wick.append([])
        d = 1
    else:
        wick.append(t2)
        wick.append([])
        d = 0
    
    for i in wittable:
        if i[1][:2:] != prt:
            wick.append(teams[0][d])
            prt = i[1][:2:]
            wick.append([])
        wi = {}
        wi['over'] = i[-1]
        a = "SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID = %s"
        iplcursor.execute(a, (i[1],))
        name = iplcursor.fetchall()[0][0]
        a2 = "SELECT RUNS FROM SCORE WHERE OVER_BALL = %s AND MATCH_ID = %s AND TEAM = %s"
        iplcursor.execute(a2, (i[-1], match_id, wick[-2]))
        score = ""
        try:
            score = iplcursor.fetchall()[0][0]
        except:
            pass
        wi['score'] = score
        wi['wicks'] = i[2]
        wi['name'] = name
        wick[-1].append(wi)
    
    if len(wick) > 1:
        wick[1].sort(key=lambda i: i['wicks'])
    if len(wick) > 3:
        wick[-1].sort(key=lambda i: i['wicks'])
    
    return wick


def db_to_plyr(name, team):
    """Search players in database."""
    sql = "SELECT * FROM PLAYER WHERE PLAYER_NAME LIKE %s AND PLAYER_ID LIKE %s"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql, (f'%{name}%', f'%{team}%'))
    players = iplcursor.fetchall()
    return players


def plr(id):
    """Get single player by ID."""
    sql = "SELECT * FROM PLAYER WHERE PLAYER_ID = %s"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql, (id,))
    player = iplcursor.fetchall()[0]
    return player


def db_to_scr(match_id, team1, team2):
    """Get scores for both teams."""
    sql = "SELECT * FROM SCORE WHERE MATCH_ID = %s AND TEAM = %s"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql, (match_id, team1))
    scores1 = iplcursor.fetchall()
    iplcursor.execute(sql, (match_id, team2))
    scores2 = iplcursor.fetchall()
    scores1.sort(key=lambda i: float(i[0]))
    scores2.sort(key=lambda i: float(i[0]))
    
    for i in scores1:
        i = list(i)
        sql4 = "SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID = %s"
        iplcursor.execute(sql4, (i[2],))
        i[2] = iplcursor.fetchall()[0][0]
        iplcursor.execute(sql4, (i[3],))
        i[3] = iplcursor.fetchall()[0][0]
        iplcursor.execute(sql4, (i[4],))
        i[4] = iplcursor.fetchall()[0][0]
    
    for i in scores2:
        i = list(i)
        sql4 = "SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID = %s"
        iplcursor.execute(sql4, (i[2],))
        i[2] = iplcursor.fetchall()[0][0]
        iplcursor.execute(sql4, (i[3],))
        i[3] = iplcursor.fetchall()[0][0]
        iplcursor.execute(sql4, (i[4],))
        i[4] = iplcursor.fetchall()[0][0]
    
    scores = {team1: scores1, team2: scores2}
    return scores


def db_to_scr1(match_id, team, over):
    """Get score for specific over."""
    sql = "SELECT * FROM SCORE WHERE MATCH_ID = %s AND TEAM = %s AND OVER_BALL = %s"
    iplcursor = myconn.cursor()
    iplcursor.execute(sql, (match_id, team, over))
    score = []
    try:
        score = iplcursor.fetchall()[0]
    except:
        pass
    score = list(score)
    
    try:
        sql4 = "SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID = %s"
        iplcursor.execute(sql4, (score[2],))
        score[2] = iplcursor.fetchall()[0][0]
    except:
        pass
    try:
        iplcursor.execute(sql4, (score[3],))
        score[3] = iplcursor.fetchall()[0][0]
    except:
        pass
    try:
        iplcursor.execute(sql4, (score[4],))
        score[4] = iplcursor.fetchall()[0][0]
    except:
        pass
    
    return score


def getts(id):
    """Get team names for a match."""
    iplcursor = myconn.cursor()
    sql3 = "SELECT TEAM_1, TEAM_2 FROM MATCHH WHERE MATCH_ID = %s"
    iplcursor.execute(sql3, (id,))
    teams = iplcursor.fetchall()
    t1 = teams[0][0]
    t2 = teams[0][1]
    return t1, t2


def db_to_scr2(match_id, team1, team2):
    """Get final score summary for match."""
    mycursor = myconn.cursor()
    final_score = {'inning1': {}, 'inning2': {}}
    
    mycursor.execute("SELECT * FROM SCORE WHERE MATCH_ID = %s AND RRR IS NULL", (match_id,))
    data = mycursor.fetchall()
    if not data:
        return final_score
    
    lst_ball = max(data, key=lambda i: float(i[0]))[0]
    mycursor.execute(
        "SELECT RUNS, WICKET, TEAM FROM SCORE WHERE MATCH_ID = %s AND OVER_BALL = %s AND RRR IS NULL",
        (match_id, str(lst_ball))
    )
    inn1_data = mycursor.fetchall()
    if not inn1_data:
        return final_score
    
    final_score['inning1']['runs'] = inn1_data[0][0]
    final_score['inning1']['wicket'] = inn1_data[0][1]
    final_score['inning1']['team'] = inn1_data[0][2]
    final_score['inning1']['over_ball'] = lst_ball

    mycursor.execute("SELECT * FROM SCORE WHERE MATCH_ID = %s AND TEAM != %s", (match_id, inn1_data[0][2]))
    data = mycursor.fetchall()
    if not data:
        return final_score
    
    lst_ball = max(data, key=lambda i: float(i[0]))[0]
    mycursor.execute(
        "SELECT * FROM SCORE WHERE MATCH_ID = %s AND OVER_BALL = %s AND TEAM <> %s",
        (match_id, lst_ball, inn1_data[0][2])
    )
    inn2_data = mycursor.fetchall()
    if not inn2_data:
        return final_score
    
    final_score['inning2']['team'] = inn2_data[0][5]
    final_score['inning2']['runs'] = inn2_data[0][6]
    final_score['inning2']['wickets'] = inn2_data[0][7]
    final_score['inning2']['over_ball'] = inn2_data[0][0]

    mycursor.execute("SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID = %s", (inn2_data[0][2],))
    final_score['inning2']['bat1'] = mycursor.fetchall()[0][0]

    mycursor.execute("SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID = %s", (inn2_data[0][3],))
    final_score['inning2']['bat2'] = mycursor.fetchall()[0][0]

    mycursor.execute("SELECT PLAYER_NAME FROM PLAYER WHERE PLAYER_ID = %s", (inn2_data[0][4],))
    final_score['inning2']['bowl'] = mycursor.fetchall()[0][0]

    mycursor.execute("SELECT * FROM BATSMAN WHERE MATCH_ID = %s AND PLAYER_ID = %s", (match_id, inn2_data[0][2]))
    bat1 = mycursor.fetchall()
    final_score['inning2']['run1'] = bat1[0][3]
    final_score['inning2']['balls_faced_1'] = bat1[0][5]

    mycursor.execute("SELECT * FROM BATSMAN WHERE MATCH_ID = %s AND PLAYER_ID = %s", (match_id, inn2_data[0][3]))
    bat2 = mycursor.fetchall()
    final_score['inning2']['run2'] = bat2[0][3]
    final_score['inning2']['balls_faced_2'] = bat2[0][5]

    mycursor.execute("SELECT * FROM BOWLER WHERE MATCH_ID = %s AND PLAYER_ID = %s", (match_id, inn2_data[0][4]))
    bowl = mycursor.fetchall()
    try:
        final_score['inning2']['bowl_wick'] = bowl[0][2]
        final_score['inning2']['balls_run'] = bowl[0][6]
    except:
        pass
    
    overs = final_score['inning2']['over_ball']
    over = int(float(overs))
    if float(overs) != int(float(overs)):
        ball = float(overs) - int(float(overs))
        ball /= 0.6
        over += ball
    final_score['inning2']['crr'] = round(final_score['inning2']['runs'] / over, 2)
    
    return final_score


def get_player_stats():
    """Get player statistics from database (replaces IPLive methods)."""
    mycursor = myconn.cursor()
    stats = {}
    
    # Orange cap (most runs)
    mycursor.execute("SELECT PLAYER_NAME FROM PLAYER WHERE RUNS = (SELECT MAX(RUNS) FROM PLAYER WHERE RUNS > 0)")
    result = mycursor.fetchall()
    stats['orange_cap'] = result[0][0] if result else ""
    
    # Purple cap (most wickets)
    mycursor.execute("SELECT PLAYER_NAME FROM PLAYER WHERE WICKET = (SELECT MAX(WICKET) FROM PLAYER WHERE WICKET > 0)")
    result = mycursor.fetchall()
    stats['purple_cap'] = result[0][0] if result else ""
    
    # Best economy
    mycursor.execute("SELECT PLAYER_NAME FROM PLAYER WHERE ECONOMY = (SELECT MIN(ECONOMY) FROM PLAYER WHERE ECONOMY > 0)")
    result = mycursor.fetchall()
    stats['best_economy'] = result[0][0] if result else ""
    
    # Best strike rate (batting)
    mycursor.execute("SELECT PLAYER_NAME FROM PLAYER WHERE BATTING_STRIKE_RATE = (SELECT MAX(BATTING_STRIKE_RATE) FROM PLAYER WHERE BATTING_STRIKE_RATE > 0)")
    result = mycursor.fetchall()
    stats['best_strike_rate'] = result[0][0] if result else ""
    
    # Best bowling strike rate
    mycursor.execute("SELECT PLAYER_NAME FROM PLAYER WHERE BOWLING_STRIKE_RATE = (SELECT MIN(BOWLING_STRIKE_RATE) FROM PLAYER WHERE BOWLING_STRIKE_RATE > 0)")
    result = mycursor.fetchall()
    stats['bowling_strike_rate'] = result[0][0] if result else ""
    
    # Best bowling average
    mycursor.execute("SELECT PLAYER_NAME FROM PLAYER WHERE BOWLING_AVERAGE = (SELECT MIN(BOWLING_AVERAGE) FROM PLAYER WHERE BOWLING_AVERAGE > 0)")
    result = mycursor.fetchall()
    stats['bowling_average'] = result[0][0] if result else ""
    
    # Best batting average
    mycursor.execute("SELECT PLAYER_NAME FROM PLAYER WHERE BATTING_AVERAGE = (SELECT MAX(BATTING_AVERAGE) FROM PLAYER WHERE BATTING_AVERAGE > 0)")
    result = mycursor.fetchall()
    stats['batting_average'] = result[0][0] if result else ""
    
    return stats


# Flask Application
app = Flask(__name__)


@app.route('/')
def index():
    """Home page with live/mock score."""
    matchid = do_it()
    sc = c.scorecard(matchid)
    pr_in = {}
    bowl_tbl = []
    bat_t = []
    w_t = []
    
    if sc.get('scorecard') and len(sc['scorecard']) > 0:
        pr_in = prv_inn(sc)
        bowl_tbl = db_to_bowl(matchid)
        bat_t = db_to_bat(matchid)
        w_t = db_to_wick(matchid)
    
    return render_template('index.html', ls=live_score, prin=pr_in, bt=bowl_tbl, batt=bat_t, wt=w_t)


@app.route('/archive/')
def archive():
    """Archive page with list of matches."""
    m_tb = db_to_match()
    return render_template('archive.html', mtb=m_tb)


@app.route('/archive/match')
def matchc():
    """Single match details."""
    id = request.args.get('id', default="", type=str)
    bat_t = db_to_bat(id)
    bowl_tbl = db_to_bowl(id)
    w_t = db_to_wick(id)
    f_s = {}
    try:
        if len(bat_t) >= 3:
            f_s = db_to_scr2(id, bat_t[0], bat_t[2])
    except:
        pass
    return render_template('match.html', batt=bat_t, bt=bowl_tbl, wt=w_t, fs=f_s)


@app.route('/playerstats/', methods=['GET', 'POST'])
def player():
    """Player statistics page."""
    teams = ['MI', 'CSK', 'DC', 'KXIP', 'SRH', 'KKR', 'RR', 'RCB']
    plyrs = db_to_plyr("", "")
    
    # Get stats from database (replaces IPLive class methods)
    stats = get_player_stats()
    o_c = stats.get('orange_cap', '')
    p_c = stats.get('purple_cap', '')
    b_e = stats.get('best_economy', '')
    s_r = stats.get('best_strike_rate', '')
    b_sr = stats.get('bowling_strike_rate', '')
    b_a = stats.get('bowling_average', '')
    a = stats.get('batting_average', '')
    
    if request.method == 'POST':
        try:
            plname = request.form['plyr']
            plteam = request.form['team']
            plyrs = db_to_plyr(plname, plteam)
        except:
            pass
    
    return render_template('playerstat.html', pls=plyrs, ts=teams, oc=o_c, pc=p_c, be=b_e, sr=s_r, bsr=b_sr, bav=b_a, av=a)


@app.route('/playerstats/player')
def playerst():
    """Individual player page."""
    id = request.args.get('id', default="", type=str)
    pl_r = plr(id)
    teams = ['MI', 'CSK', 'DC', 'KXIP', 'SRH', 'KKR', 'RR', 'RCB']
    return render_template('player.html', player=pl_r, ts=teams)


@app.route('/archive/score', methods=['GET', 'POST'])
def score_bb():
    """Ball-by-ball score page."""
    id = request.args.get('id', default="", type=str)
    team1, team2 = getts(id)
    scrs = db_to_scr(id, team1, team2)
    
    if request.method == 'POST':
        scrover = request.form['over']
        scrteam = request.form['team']
        scr = db_to_scr1(id, scrteam, scrover)
        return render_template('score.html', scores=scrs, score=scr, match=id)
    else:
        return render_template('score.html', scores=scrs, score=[], match=id)


if __name__ == "__main__":
    app.run(debug=True)
