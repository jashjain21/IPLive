#!/usr/bin/env python3
"""
Seed data script for IPLive - Populates MySQL database with sample cricket data.
Run this to set up the database for offline/demo mode.

Usage:
    python seed_data.py

Requires MySQL database 'scratch' to exist.
"""
import mysql.connector
import os

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'password'),
    'database': os.environ.get('DB_NAME', 'scratch')
}

# Team abbreviations
TEAMS = ['CSK', 'MI', 'RCB', 'KKR', 'SRH', 'KXIP', 'DC', 'RR']

# Player data for each team
PLAYERS = {
    'CSK': [
        ('CSK01', 'Ruturaj Gaikwad'),
        ('CSK02', 'Devon Conway'),
        ('CSK03', 'Moeen Ali'),
        ('CSK04', 'Shivam Dube'),
        ('CSK05', 'Ravindra Jadeja'),
        ('CSK06', 'MS Dhoni'),
        ('CSK07', 'Deepak Chahar'),
        ('CSK08', 'Matheesha Pathirana'),
        ('CSK09', 'Maheesh Theekshana'),
        ('CSK10', 'Tushar Deshpande'),
        ('CSK11', 'Ajinkya Rahane'),
    ],
    'MI': [
        ('MI01', 'Rohit Sharma'),
        ('MI02', 'Ishan Kishan'),
        ('MI03', 'Suryakumar Yadav'),
        ('MI04', 'Hardik Pandya'),
        ('MI05', 'Kieron Pollard'),
        ('MI06', 'Jasprit Bumrah'),
        ('MI07', 'Jofra Archer'),
        ('MI08', 'Piyush Chawla'),
        ('MI09', 'Tim David'),
        ('MI10', 'Tilak Varma'),
        ('MI11', 'Nehal Wadhera'),
    ],
    'RCB': [
        ('RCB01', 'Virat Kohli'),
        ('RCB02', 'Faf du Plessis'),
        ('RCB03', 'Glenn Maxwell'),
        ('RCB04', 'Rajat Patidar'),
        ('RCB05', 'Dinesh Karthik'),
        ('RCB06', 'Mohammed Siraj'),
        ('RCB07', 'Josh Hazlewood'),
        ('RCB08', 'Wanindu Hasaranga'),
        ('RCB09', 'Harshal Patel'),
        ('RCB10', 'Shahbaz Ahmed'),
        ('RCB11', 'Anuj Rawat'),
    ],
    'KKR': [
        ('KKR01', 'Shreyas Iyer'),
        ('KKR02', 'Venkatesh Iyer'),
        ('KKR03', 'Andre Russell'),
        ('KKR04', 'Sunil Narine'),
        ('KKR05', 'Varun Chakravarthy'),
        ('KKR06', 'Shardul Thakur'),
        ('KKR07', 'Nitish Rana'),
        ('KKR08', 'Rinku Singh'),
        ('KKR09', 'Tim Southee'),
        ('KKR10', 'Rahmanullah Gurbaz'),
        ('KKR11', 'Umesh Yadav'),
    ],
    'SRH': [
        ('SRH01', 'Aiden Markram'),
        ('SRH02', 'Heinrich Klaasen'),
        ('SRH03', 'Travis Head'),
        ('SRH04', 'Abdul Samad'),
        ('SRH05', 'Rahul Tripathi'),
        ('SRH06', 'Bhuvneshwar Kumar'),
        ('SRH07', 'Marco Jansen'),
        ('SRH08', 'Washington Sundar'),
        ('SRH09', 'Umran Malik'),
        ('SRH10', 'Pat Cummins'),
        ('SRH11', 'Mayank Agarwal'),
    ],
    'KXIP': [
        ('KXIP01', 'Shikhar Dhawan'),
        ('KXIP02', 'Jonny Bairstow'),
        ('KXIP03', 'Liam Livingstone'),
        ('KXIP04', 'Sam Curran'),
        ('KXIP05', 'Shahrukh Khan'),
        ('KXIP06', 'Arshdeep Singh'),
        ('KXIP07', 'Kagiso Rabada'),
        ('KXIP08', 'Rahul Chahar'),
        ('KXIP09', 'Nathan Ellis'),
        ('KXIP10', 'Prabhsimran Singh'),
        ('KXIP11', 'Harpreet Brar'),
    ],
    'DC': [
        ('DC01', 'David Warner'),
        ('DC02', 'Mitchell Marsh'),
        ('DC03', 'Rishabh Pant'),
        ('DC04', 'Axar Patel'),
        ('DC05', 'Kuldeep Yadav'),
        ('DC06', 'Anrich Nortje'),
        ('DC07', 'Ishant Sharma'),
        ('DC08', 'Prithvi Shaw'),
        ('DC09', 'Sarfaraz Khan'),
        ('DC10', 'Mukesh Kumar'),
        ('DC11', 'Rovman Powell'),
    ],
    'RR': [
        ('RR01', 'Sanju Samson'),
        ('RR02', 'Jos Buttler'),
        ('RR03', 'Yashasvi Jaiswal'),
        ('RR04', 'Shimron Hetmyer'),
        ('RR05', 'Riyan Parag'),
        ('RR06', 'Trent Boult'),
        ('RR07', 'Yuzvendra Chahal'),
        ('RR08', 'Prasidh Krishna'),
        ('RR09', 'R Ashwin'),
        ('RR10', 'Devdutt Padikkal'),
        ('RR11', 'Obed McCoy'),
    ],
}

# Sample match data
MATCHES = [
    ('M001', 'CSK', 'MI', 'Wankhede Stadium, Mumbai', '2020-09-19', 'CSK won by 5 wickets'),
    ('M002', 'RCB', 'KKR', 'M. Chinnaswamy Stadium, Bangalore', '2020-09-20', 'RCB won by 8 runs'),
    ('M003', 'DC', 'KXIP', 'Dubai International Stadium', '2020-09-21', 'DC won by 44 runs'),
    ('M004', 'SRH', 'RR', 'Dubai International Stadium', '2020-09-22', 'RR won by 6 wickets'),
    ('M005', 'MI', 'RCB', 'Sheikh Zayed Stadium, Abu Dhabi', '2020-09-23', 'MI won by 5 wickets'),
]

# Sample batsman data (player_id, match_id, position, runs, strike_rate, balls, boundaries, fours, sixes)
BATSMEN = [
    # M001 - CSK innings
    ('CSK01', 'M001', 1, 65, 154.76, 42, 10, 7, 3),
    ('CSK02', 'M001', 2, 45, 140.62, 32, 6, 4, 2),
    ('CSK03', 'M001', 3, 32, 177.77, 18, 4, 2, 2),
    ('CSK04', 'M001', 4, 25, 166.66, 15, 3, 1, 2),
    ('CSK05', 'M001', 5, 8, 133.33, 6, 1, 1, 0),
    # M001 - MI innings
    ('MI01', 'M001', 1, 55, 144.73, 38, 8, 6, 2),
    ('MI02', 'M001', 2, 35, 125.00, 28, 4, 3, 1),
    ('MI03', 'M001', 3, 42, 161.53, 26, 6, 4, 2),
    ('MI04', 'M001', 4, 22, 146.66, 15, 3, 2, 1),
    ('MI05', 'M001', 5, 12, 150.00, 8, 1, 1, 0),
    # M002 - RCB innings
    ('RCB01', 'M002', 1, 75, 156.25, 48, 10, 8, 2),
    ('RCB02', 'M002', 2, 48, 137.14, 35, 6, 5, 1),
    ('RCB03', 'M002', 3, 35, 175.00, 20, 5, 2, 3),
    ('RCB04', 'M002', 4, 18, 150.00, 12, 2, 2, 0),
    # M002 - KKR innings
    ('KKR01', 'M002', 1, 62, 137.77, 45, 8, 5, 3),
    ('KKR02', 'M002', 2, 38, 135.71, 28, 5, 4, 1),
    ('KKR03', 'M002', 3, 45, 204.54, 22, 7, 3, 4),
    ('KKR04', 'M002', 4, 18, 150.00, 12, 2, 1, 1),
]

# Sample bowler data (player_id, match_id, wickets, economy, avg, strike_rate, runs, overs)
BOWLERS = [
    # M001 - MI bowling
    ('MI06', 'M001', 2, 7.00, 14.00, 12.0, 28, 4.0),
    ('MI07', 'M001', 1, 8.75, 35.00, 24.0, 35, 4.0),
    ('MI04', 'M001', 1, 9.00, 30.00, 20.0, 30, 3.2),
    ('MI08', 'M001', 0, 10.50, None, None, 42, 4.0),
    ('MI05', 'M001', 1, 11.25, 45.00, 24.0, 45, 4.0),
    # M001 - CSK bowling
    ('CSK07', 'M001', 3, 8.00, 10.66, 8.0, 32, 4.0),
    ('CSK08', 'M001', 2, 9.50, 19.00, 12.0, 38, 4.0),
    ('CSK05', 'M001', 1, 7.00, 28.00, 24.0, 28, 4.0),
    ('CSK09', 'M001', 2, 8.75, 17.50, 12.0, 35, 4.0),
    ('CSK10', 'M001', 0, 10.50, None, None, 42, 4.0),
    # M002 - KKR bowling  
    ('KKR04', 'M002', 2, 8.00, 16.00, 12.0, 32, 4.0),
    ('KKR05', 'M002', 2, 7.00, 14.00, 12.0, 28, 4.0),
    ('KKR03', 'M002', 1, 10.00, 40.00, 24.0, 40, 4.0),
    ('KKR06', 'M002', 1, 11.25, 45.00, 24.0, 45, 4.0),
    # M002 - RCB bowling
    ('RCB06', 'M002', 3, 8.75, 11.66, 8.0, 35, 4.0),
    ('RCB07', 'M002', 2, 8.00, 16.00, 12.0, 32, 4.0),
    ('RCB08', 'M002', 2, 9.50, 19.00, 12.0, 38, 4.0),
    ('RCB09', 'M002', 2, 10.00, 20.00, 12.0, 40, 4.0),
]


def create_tables(cursor):
    """Create database tables if they don't exist."""
    print("📋 Creating tables...")
    
    tables = [
        """CREATE TABLE IF NOT EXISTS MATCHH (
            MATCH_ID VARCHAR(20) PRIMARY KEY,
            TEAM_1 VARCHAR(10),
            TEAM_2 VARCHAR(10),
            STADIUM VARCHAR(100),
            MATCH_DATE DATE,
            RESULT VARCHAR(255)
        )""",
        """CREATE TABLE IF NOT EXISTS PLAYER (
            PLAYER_ID VARCHAR(20) PRIMARY KEY,
            PLAYER_NAME VARCHAR(100),
            RUNS INT DEFAULT 0,
            BALLS_FACED INT DEFAULT 0,
            WICKET INT DEFAULT 0,
            RUNS_CONCEDED INT DEFAULT 0,
            OVERS_BOWLED DECIMAL(5,1) DEFAULT 0,
            MATCHES_PLAYED INT DEFAULT 0,
            BATTING_STRIKE_RATE DECIMAL(6,2) DEFAULT 0,
            ECONOMY DECIMAL(5,2) DEFAULT 0,
            BOWLING_AVERAGE DECIMAL(6,2) DEFAULT 0,
            BOWLING_STRIKE_RATE DECIMAL(6,2) DEFAULT 0,
            BATTING_AVERAGE DECIMAL(6,2) DEFAULT 0
        )""",
        """CREATE TABLE IF NOT EXISTS BATSMAN (
            PLAYER_ID VARCHAR(20),
            MATCH_ID VARCHAR(20),
            POSITION INT,
            RUNS INT,
            BATTING_STRIKE_RATE DECIMAL(6,2),
            BALLS_FACED INT,
            BOUNDARIES INT,
            FOURS INT,
            SIXES INT,
            PRIMARY KEY (PLAYER_ID, MATCH_ID)
        )""",
        """CREATE TABLE IF NOT EXISTS BOWLER (
            PLAYER_ID VARCHAR(20),
            MATCH_ID VARCHAR(20),
            WICKET INT,
            ECONOMY DECIMAL(5,2),
            BOWLING_AVERAGE DECIMAL(6,2),
            BOWLING_STRIKE_RATE DECIMAL(6,2),
            RUNS_CONCEDED INT,
            OVER_BOWLED DECIMAL(4,1),
            PRIMARY KEY (PLAYER_ID, MATCH_ID)
        )""",
        """CREATE TABLE IF NOT EXISTS WICKETS (
            MATCH_ID VARCHAR(20),
            PLAYER_ID VARCHAR(20),
            WICKET_NUM INT,
            DISMISSAL VARCHAR(255),
            OVER_BALL VARCHAR(10),
            PRIMARY KEY (MATCH_ID, PLAYER_ID, WICKET_NUM)
        )""",
        """CREATE TABLE IF NOT EXISTS SCORE (
            OVER_BALL DECIMAL(4,1),
            MATCH_ID VARCHAR(20),
            BATSMAN_1_ID VARCHAR(20),
            BATSMAN_2_ID VARCHAR(20),
            BOWLER_ID VARCHAR(20),
            TEAM VARCHAR(10),
            RUNS INT,
            WICKET INT,
            RUNS_REQ INT,
            RRR DECIMAL(5,2),
            CRR DECIMAL(5,2),
            COMMENTARY TEXT,
            PRIMARY KEY (OVER_BALL, MATCH_ID, TEAM)
        )"""
    ]
    
    for sql in tables:
        cursor.execute(sql)
    print("  ✅ Tables created successfully")


def seed_players(cursor, conn):
    """Insert player data."""
    print("\n👥 Seeding players...")
    count = 0
    
    for team, players in PLAYERS.items():
        for player_id, player_name in players:
            try:
                cursor.execute(
                    "INSERT INTO PLAYER (PLAYER_ID, PLAYER_NAME) VALUES (%s, %s)",
                    (player_id, player_name)
                )
                count += 1
            except mysql.connector.IntegrityError:
                pass  # Player already exists
    
    conn.commit()
    print(f"  ✅ Seeded {count} players")


def seed_matches(cursor, conn):
    """Insert match data."""
    print("\n🏏 Seeding matches...")
    count = 0
    
    for match in MATCHES:
        try:
            cursor.execute(
                "INSERT INTO MATCHH VALUES (%s, %s, %s, %s, %s, %s)",
                match
            )
            count += 1
        except mysql.connector.IntegrityError:
            pass  # Match already exists
    
    conn.commit()
    print(f"  ✅ Seeded {count} matches")


def seed_batsmen(cursor, conn):
    """Insert batsman statistics."""
    print("\n🏑 Seeding batsman stats...")
    count = 0
    
    for bat in BATSMEN:
        try:
            cursor.execute(
                "INSERT INTO BATSMAN VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                bat
            )
            count += 1
        except mysql.connector.IntegrityError:
            pass
    
    conn.commit()
    print(f"  ✅ Seeded {count} batsman records")


def seed_bowlers(cursor, conn):
    """Insert bowler statistics."""
    print("\n🎯 Seeding bowler stats...")
    count = 0
    
    for bowl in BOWLERS:
        try:
            cursor.execute(
                "INSERT INTO BOWLER VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                bowl
            )
            count += 1
        except mysql.connector.IntegrityError:
            pass
    
    conn.commit()
    print(f"  ✅ Seeded {count} bowler records")


def update_player_stats(cursor, conn):
    """Update cumulative player statistics."""
    print("\n📊 Updating player aggregate stats...")
    
    # Update batting stats
    cursor.execute("""
        UPDATE PLAYER p
        SET 
            RUNS = COALESCE((SELECT SUM(RUNS) FROM BATSMAN WHERE PLAYER_ID = p.PLAYER_ID), 0),
            BALLS_FACED = COALESCE((SELECT SUM(BALLS_FACED) FROM BATSMAN WHERE PLAYER_ID = p.PLAYER_ID), 0),
            MATCHES_PLAYED = (
                SELECT COUNT(DISTINCT MATCH_ID) FROM (
                    SELECT MATCH_ID FROM BATSMAN WHERE PLAYER_ID = p.PLAYER_ID
                    UNION
                    SELECT MATCH_ID FROM BOWLER WHERE PLAYER_ID = p.PLAYER_ID
                ) AS m
            )
    """)
    
    # Update bowling stats
    cursor.execute("""
        UPDATE PLAYER p
        SET 
            WICKET = COALESCE((SELECT SUM(WICKET) FROM BOWLER WHERE PLAYER_ID = p.PLAYER_ID), 0),
            RUNS_CONCEDED = COALESCE((SELECT SUM(RUNS_CONCEDED) FROM BOWLER WHERE PLAYER_ID = p.PLAYER_ID), 0),
            OVERS_BOWLED = COALESCE((SELECT SUM(OVER_BOWLED) FROM BOWLER WHERE PLAYER_ID = p.PLAYER_ID), 0)
    """)
    
    # Calculate derived stats
    cursor.execute("""
        UPDATE PLAYER 
        SET BATTING_STRIKE_RATE = CASE WHEN BALLS_FACED > 0 THEN (RUNS * 100.0 / BALLS_FACED) ELSE 0 END
    """)
    
    cursor.execute("""
        UPDATE PLAYER 
        SET ECONOMY = CASE WHEN OVERS_BOWLED > 0 THEN (RUNS_CONCEDED / OVERS_BOWLED) ELSE 0 END
    """)
    
    conn.commit()
    print("  ✅ Player stats updated")


def print_summary(cursor):
    """Print summary of seeded data."""
    print("\n" + "="*50)
    print("📊 SEED DATA SUMMARY")
    print("="*50)
    
    cursor.execute("SELECT COUNT(*) FROM PLAYER")
    print(f"  Players: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM MATCHH")
    print(f"  Matches: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM BATSMAN")
    print(f"  Batsman records: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM BOWLER")
    print(f"  Bowler records: {cursor.fetchone()[0]}")
    
    # Top run scorers
    print("\n🏆 Top Run Scorers:")
    cursor.execute("SELECT PLAYER_NAME, RUNS FROM PLAYER WHERE RUNS > 0 ORDER BY RUNS DESC LIMIT 5")
    for row in cursor.fetchall():
        print(f"    {row[0]}: {row[1]} runs")
    
    # Top wicket takers
    print("\n🎯 Top Wicket Takers:")
    cursor.execute("SELECT PLAYER_NAME, WICKET FROM PLAYER WHERE WICKET > 0 ORDER BY WICKET DESC LIMIT 5")
    for row in cursor.fetchall():
        print(f"    {row[0]}: {row[1]} wickets")
    
    print("\n" + "="*50)


def main():
    """Main function to seed the database."""
    print("\n" + "="*50)
    print("🌱 IPLive - DATABASE SEED SCRIPT")
    print("="*50)
    
    print(f"\n📡 Connecting to database: {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("  ✅ Connected successfully")
        
        create_tables(cursor)
        seed_players(cursor, conn)
        seed_matches(cursor, conn)
        seed_batsmen(cursor, conn)
        seed_bowlers(cursor, conn)
        update_player_stats(cursor, conn)
        print_summary(cursor)
        
        cursor.close()
        conn.close()
        
        print("\n✅ Database seeding completed successfully!")
        print("   You can now run the app in offline/mock mode.")
        
    except mysql.connector.Error as err:
        print(f"\n❌ Database error: {err}")
        print("\nMake sure:")
        print("  1. MySQL is running")
        print("  2. Database 'scratch' exists: CREATE DATABASE scratch;")
        print("  3. User credentials are correct")
        raise


if __name__ == '__main__':
    main()
