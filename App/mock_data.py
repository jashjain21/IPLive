"""
Mock data module for IPLive - Offline mode without external API calls.
This replaces pycricbuzz API calls with pre-seeded database data.
"""
from datetime import date
from typing import Dict, List, Any, Optional

# Mock match data - simulates data that would come from pycricbuzz
MOCK_MATCHES = [
    {
        'id': 'M001',
        'srs': 'Indian Premier League 2020',
        'start_time': f'{date.today()} 19:30',
        'team1': {'name': 'Chennai Super Kings'},
        'team2': {'name': 'Mumbai Indians'},
        'venue_name': 'Wankhede Stadium, Mumbai',
        'status': 'CSK won by 5 wickets'
    },
    {
        'id': 'M002',
        'srs': 'Indian Premier League 2020',
        'start_time': f'{date.today()} 15:30',
        'team1': {'name': 'Royal Challengers Bangalore'},
        'team2': {'name': 'Kolkata Knight Riders'},
        'venue_name': 'M. Chinnaswamy Stadium, Bangalore',
        'status': 'RCB won by 8 runs'
    },
]

# Mock scorecard data
MOCK_SCORECARDS = {
    'M001': {
        'scorecard': [
            {
                'batteam': 'Chennai Super Kings',
                'bowlteam': 'Mumbai Indians',
                'runs': '180',
                'wickets': '5',
                'overs': '19.2',
                'inng_num': '2',
                'batcard': [
                    {'name': 'Ruturaj Gaikwad', 'runs': '65', 'balls': '42', 'fours': '7', 'six': '3', 'dismissal': 'not out'},
                    {'name': 'Devon Conway', 'runs': '45', 'balls': '32', 'fours': '4', 'six': '2', 'dismissal': 'c Rohit b Bumrah'},
                    {'name': 'Moeen Ali', 'runs': '32', 'balls': '18', 'fours': '2', 'six': '2', 'dismissal': 'batting'},
                    {'name': 'Shivam Dube', 'runs': '25', 'balls': '15', 'fours': '1', 'six': '2', 'dismissal': 'b Archer'},
                    {'name': 'Ravindra Jadeja', 'runs': '8', 'balls': '6', 'fours': '1', 'six': '0', 'dismissal': 'run out'},
                ],
                'bowlcard': [
                    {'name': 'Jasprit Bumrah', 'overs': '4', 'runs': '28', 'wickets': '2'},
                    {'name': 'Jofra Archer', 'overs': '4', 'runs': '35', 'wickets': '1'},
                    {'name': 'Hardik Pandya', 'overs': '3.2', 'runs': '30', 'wickets': '1'},
                    {'name': 'Piyush Chawla', 'overs': '4', 'runs': '42', 'wickets': '0'},
                    {'name': 'Kieron Pollard', 'overs': '4', 'runs': '45', 'wickets': '1'},
                ],
                'fall_wickets': [
                    {'name': 'Devon Conway', 'wkt_num': '1', 'overs': '8.3'},
                    {'name': 'Shivam Dube', 'wkt_num': '2', 'overs': '12.1'},
                    {'name': 'Ravindra Jadeja', 'wkt_num': '3', 'overs': '15.4'},
                ]
            },
            {
                'batteam': 'Mumbai Indians',
                'bowlteam': 'Chennai Super Kings',
                'runs': '175',
                'wickets': '8',
                'overs': '20',
                'inng_num': '1',
                'batcard': [
                    {'name': 'Rohit Sharma', 'runs': '55', 'balls': '38', 'fours': '6', 'six': '2', 'dismissal': 'c Jadeja b Chahar'},
                    {'name': 'Ishan Kishan', 'runs': '35', 'balls': '28', 'fours': '3', 'six': '1', 'dismissal': 'b Theekshana'},
                    {'name': 'Suryakumar Yadav', 'runs': '42', 'balls': '26', 'fours': '4', 'six': '2', 'dismissal': 'c Conway b Jadeja'},
                    {'name': 'Hardik Pandya', 'runs': '22', 'balls': '15', 'fours': '2', 'six': '1', 'dismissal': 'not out'},
                    {'name': 'Kieron Pollard', 'runs': '12', 'balls': '8', 'fours': '1', 'six': '0', 'dismissal': 'b Chahar'},
                ],
                'bowlcard': [
                    {'name': 'Deepak Chahar', 'overs': '4', 'runs': '32', 'wickets': '3'},
                    {'name': 'Matheesha Pathirana', 'overs': '4', 'runs': '38', 'wickets': '2'},
                    {'name': 'Ravindra Jadeja', 'overs': '4', 'runs': '28', 'wickets': '1'},
                    {'name': 'Maheesh Theekshana', 'overs': '4', 'runs': '35', 'wickets': '2'},
                    {'name': 'Tushar Deshpande', 'overs': '4', 'runs': '42', 'wickets': '0'},
                ],
                'fall_wickets': [
                    {'name': 'Rohit Sharma', 'wkt_num': '1', 'overs': '10.2'},
                    {'name': 'Ishan Kishan', 'wkt_num': '2', 'overs': '12.4'},
                    {'name': 'Suryakumar Yadav', 'wkt_num': '3', 'overs': '15.1'},
                    {'name': 'Kieron Pollard', 'wkt_num': '4', 'overs': '18.3'},
                ]
            }
        ]
    },
    'M002': {
        'scorecard': [
            {
                'batteam': 'Royal Challengers Bangalore',
                'bowlteam': 'Kolkata Knight Riders',
                'runs': '185',
                'wickets': '6',
                'overs': '20',
                'inng_num': '2',
                'batcard': [
                    {'name': 'Virat Kohli', 'runs': '75', 'balls': '48', 'fours': '8', 'six': '2', 'dismissal': 'not out'},
                    {'name': 'Faf du Plessis', 'runs': '48', 'balls': '35', 'fours': '5', 'six': '1', 'dismissal': 'c Russell b Narine'},
                    {'name': 'Glenn Maxwell', 'runs': '35', 'balls': '20', 'fours': '2', 'six': '3', 'dismissal': 'b Varun'},
                    {'name': 'Rajat Patidar', 'runs': '18', 'balls': '12', 'fours': '2', 'six': '0', 'dismissal': 'run out'},
                ],
                'bowlcard': [
                    {'name': 'Sunil Narine', 'overs': '4', 'runs': '32', 'wickets': '2'},
                    {'name': 'Varun Chakravarthy', 'overs': '4', 'runs': '28', 'wickets': '2'},
                    {'name': 'Andre Russell', 'overs': '4', 'runs': '40', 'wickets': '1'},
                    {'name': 'Shardul Thakur', 'overs': '4', 'runs': '45', 'wickets': '1'},
                ],
                'fall_wickets': [
                    {'name': 'Faf du Plessis', 'wkt_num': '1', 'overs': '9.5'},
                    {'name': 'Glenn Maxwell', 'wkt_num': '2', 'overs': '14.2'},
                    {'name': 'Rajat Patidar', 'wkt_num': '3', 'overs': '17.1'},
                ]
            },
            {
                'batteam': 'Kolkata Knight Riders',
                'bowlteam': 'Royal Challengers Bangalore',
                'runs': '177',
                'wickets': '9',
                'overs': '20',
                'inng_num': '1',
                'batcard': [
                    {'name': 'Shreyas Iyer', 'runs': '62', 'balls': '45', 'fours': '5', 'six': '3', 'dismissal': 'c Kohli b Siraj'},
                    {'name': 'Venkatesh Iyer', 'runs': '38', 'balls': '28', 'fours': '4', 'six': '1', 'dismissal': 'b Hazlewood'},
                    {'name': 'Andre Russell', 'runs': '45', 'balls': '22', 'fours': '3', 'six': '4', 'dismissal': 'c Patidar b Siraj'},
                    {'name': 'Sunil Narine', 'runs': '18', 'balls': '12', 'fours': '1', 'six': '1', 'dismissal': 'not out'},
                ],
                'bowlcard': [
                    {'name': 'Mohammed Siraj', 'overs': '4', 'runs': '35', 'wickets': '3'},
                    {'name': 'Josh Hazlewood', 'overs': '4', 'runs': '32', 'wickets': '2'},
                    {'name': 'Wanindu Hasaranga', 'overs': '4', 'runs': '38', 'wickets': '2'},
                    {'name': 'Harshal Patel', 'overs': '4', 'runs': '40', 'wickets': '2'},
                ],
                'fall_wickets': [
                    {'name': 'Venkatesh Iyer', 'wkt_num': '1', 'overs': '7.3'},
                    {'name': 'Shreyas Iyer', 'wkt_num': '2', 'overs': '13.5'},
                    {'name': 'Andre Russell', 'wkt_num': '3', 'overs': '17.2'},
                ]
            }
        ]
    }
}

# Mock match info data
MOCK_MATCH_INFO = {
    'M001': {'mchstate': 'mom', 'status': 'CSK won by 5 wickets'},
    'M002': {'mchstate': 'mom', 'status': 'RCB won by 8 runs'},
}

# Mock commentary
MOCK_COMMENTARY = {
    'M001': {
        'commentary': [
            {'over': '19.2', 'comm': 'FOUR! Gaikwad finishes in style! CSK win!'},
            {'over': '19.1', 'comm': 'Single to deep mid-wicket'},
            {'over': '18.6', 'comm': 'SIX! Moeen Ali launches it over long-on!'},
            {'over': '18.5', 'comm': 'Dot ball, good yorker from Bumrah'},
            {'over': '18.4', 'comm': 'Single pushed to cover'},
        ]
    },
    'M002': {
        'commentary': [
            {'over': '20.0', 'comm': 'Full toss, driven to fielder. RCB win by 8 runs!'},
            {'over': '19.5', 'comm': 'WICKET! Caught at deep! KKR collapse continues'},
            {'over': '19.4', 'comm': 'SIX! Russell trying to take KKR home'},
            {'over': '19.3', 'comm': 'Single, 22 needed off 3 balls'},
            {'over': '19.2', 'comm': 'Dot ball, excellent death bowling'},
        ]
    }
}


class MockCricbuzz:
    """Mock Cricbuzz class that returns pre-defined data instead of calling external API."""
    
    def matches(self) -> List[Dict[str, Any]]:
        """Return mock list of matches."""
        return MOCK_MATCHES
    
    def scorecard(self, match_id: str) -> Dict[str, Any]:
        """Return mock scorecard for a match."""
        return MOCK_SCORECARDS.get(match_id, {'scorecard': []})
    
    def matchinfo(self, match_id: str) -> Dict[str, str]:
        """Return mock match info."""
        return MOCK_MATCH_INFO.get(match_id, {'mchstate': 'unknown', 'status': 'No data'})
    
    def commentary(self, match_id: str) -> Dict[str, List]:
        """Return mock commentary."""
        return MOCK_COMMENTARY.get(match_id, {'commentary': []})


# Live score state (for mock mode)
mock_live_score = {
    'runs': '180', 
    'wickets': '5', 
    'crr': 9.31, 
    'rrr': 'NULL',
    'req_runs': 'NULL', 
    'bat1': 'Ruturaj Gaikwad',
    'bat2': 'Moeen Ali', 
    'run1': '65',
    'run2': '32', 
    'bowl': 'Jasprit Bumrah',
    'bowl_wick': '2',
    'bowl_run': '28', 
    'team': 'CSK', 
    'over_ball': '19.2',
    'ball_faced_1': '42',
    'ball_faced_2': '18'
}


def get_mock_cricbuzz():
    """Factory function to get mock Cricbuzz instance."""
    return MockCricbuzz()
