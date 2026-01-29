from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Player:
    player_id: str
    player_name: str
    runs: Optional[int] = 0
    balls_faced: Optional[int] = 0
    wicket: Optional[int] = 0
    runs_conceded: Optional[int] = 0
    overs_bowled: Optional[float] = 0.0
    matches_played: Optional[int] = 0
    batting_strike_rate: Optional[float] = 0.0
    economy: Optional[float] = 0.0
    bowling_average: Optional[float] = 0.0
    bowling_strike_rate: Optional[float] = 0.0
    batting_average: Optional[float] = 0.0

    def __post_init__(self):
        if self.runs is not None and self.runs < 0:
            raise ValueError("Runs cannot be negative")
        if self.balls_faced is not None and self.balls_faced < 0:
            raise ValueError("Balls faced cannot be negative")
        if self.wicket is not None and self.wicket < 0:
            raise ValueError("Wickets cannot be negative")
        if self.runs_conceded is not None and self.runs_conceded < 0:
            raise ValueError("Runs conceded cannot be negative")
        if self.overs_bowled is not None and self.overs_bowled < 0:
            raise ValueError("Overs bowled cannot be negative")
        if self.matches_played is not None and self.matches_played < 0:
            raise ValueError("Matches played cannot be negative")

@dataclass
class Match:
    match_id: str
    team1: str
    team2: str
    stadium: str
    date: str
    result: str

    def __post_init__(self):
        if not self.match_id:
            raise ValueError("Match ID cannot be empty")
        if not self.team1 or not self.team2:
            raise ValueError("Teams cannot be empty")

@dataclass
class BattingStat:
    player_id: str
    match_id: str
    position: int
    runs: int
    strike_rate: float
    balls: int
    boundaries: int
    fours: int
    sixes: int

    def __post_init__(self):
        if self.position < 1:
            raise ValueError("Position must be positive")
        if self.runs < 0 or self.balls < 0 or self.boundaries < 0 or self.fours < 0 or self.sixes < 0:
            raise ValueError("Stats cannot be negative")

@dataclass
class BowlingStat:
    player_id: str
    match_id: str
    wickets: int
    economy: float
    average: float
    strike_rate: float
    runs_conceded: int
    overs: float

    def __post_init__(self):
        if self.wickets < 0 or self.runs_conceded < 0 or self.overs < 0:
            raise ValueError("Stats cannot be negative")