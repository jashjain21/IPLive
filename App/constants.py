from enum import Enum

class Team(Enum):
    CSK = "CSK"
    MI = "MI"
    RCB = "RCB"
    KKR = "KKR"
    SRH = "SRH"
    KXIP = "KXIP"
    DC = "DC"
    RR = "RR"

TEAM_MAPPING = {
    "Chennai Super Kings": Team.CSK.value,
    "Mumbai Indians": Team.MI.value,
    "Royal Challengers Bangalore": Team.RCB.value,
    "Kolkata Knight Riders": Team.KKR.value,
    "Sunrisers Hyderabad": Team.SRH.value,
    "Kings XI Punjab": Team.KXIP.value,
    "Delhi Capitals": Team.DC.value,
    "Rajasthan Royals": Team.RR.value,
}

ALL_TEAMS = [team.value for team in Team]

class Table:
    MATCHH = "MATCHH"
    PLAYER = "PLAYER"
    BATSMAN = "BATSMAN"
    BOWLER = "BOWLER"
    WICKETS = "WICKETS"
    SCORE = "SCORE"