import pytest
from unittest.mock import MagicMock, patch
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
from App.models import Player, Match


class TestRepository:
    def test_get_all_matches_success(self, mock_db_manager, mock_cursor):
        """Test get_all_matches with successful data."""
        mock_cursor.fetchall.return_value = [
            ('M001', 'CSK', 'MI', 'Stadium', '2020-01-01', 'CSK won'),
            ('M002', 'RCB', 'KKR', 'Stadium2', '2020-01-02', 'RCB won')
        ]

        result = get_all_matches()

        assert len(result) == 2
        assert isinstance(result[0], Match)
        assert result[0].match_id == 'M002'
        assert result[0].team1 == 'RCB'  # Verify correct order
        assert result[0].team1 == 'CSK'
        mock_cursor.execute.assert_called()

    def test_get_all_matches_no_data(self, mock_db_manager, mock_cursor):
        """Test get_all_matches with no data."""
        mock_cursor.fetchall.return_value = []

        result = get_all_matches()

        assert result == []

    def test_get_all_matches_db_error(self, mock_db_manager, mock_cursor):
        """Test get_all_matches with database error."""
        mock_cursor.execute.side_effect = Exception("DB Error")

        result = get_all_matches()

        assert result == []

    def test_get_player_by_id_success(self, mock_db_manager, mock_cursor):
        """Test get_player_by_id with valid data."""
        mock_cursor.fetchall.return_value = [('CSK01', 'Player1', 100, 50, 5, 200, 10.0, 10, 2.0, 5.0, 20.0, 15.0, 10.0)]

        result = get_player_by_id('CSK01')

        assert isinstance(result, Player)
        assert result.player_id == 'CSK01'
        assert result.player_name == 'Player1'

    def test_get_player_by_id_not_found(self, mock_db_manager, mock_cursor):
        """Test get_player_by_id with no data."""
        mock_cursor.fetchall.return_value = []

        result = get_player_by_id('INVALID')

        assert result is None

    def test_search_players_success(self, mock_db_manager, mock_cursor):
        """Test search_players with results."""
        mock_cursor.fetchall.return_value = [
            ('CSK01', 'Player1', 100, 50, 5, 200, 10.0, 10, 2.0, 5.0, 20.0, 15.0, 10.0),
            ('MI01', 'Player2', 150, 75, 7, 250, 12.0, 12, 2.5, 6.0, 25.0, 18.0, 12.5)
        ]

        result = search_players('Player', 'CSK')

        assert len(result) == 2
        assert all(isinstance(p, Player) for p in result)

    def test_search_players_empty(self, mock_db_manager, mock_cursor):
        """Test search_players with no results."""
        mock_cursor.fetchall.return_value = []

        result = search_players('NonExistent', 'XYZ')

        assert result == []

    def test_get_bowling_stats_by_match_success(self, mock_db_manager, mock_cursor):
        """Test get_bowling_stats_by_match with data."""
        mock_cursor.fetchall.side_effect = [
            [('CSK01', 'M001', 2, 7.0, 14.0, 12.0, 28, 4.0)],  # bowtable
            [('Player1',)]  # name query
        ]

        result = get_bowling_stats_by_match('M001')

        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_batting_stats_by_match_success(self, mock_db_manager, mock_cursor):
        """Test get_batting_stats_by_match with data."""
        mock_cursor.fetchall.side_effect = [
            [('CSK01', 'M001', 1, 65, 154.76, 42, 10, 7, 3)],  # batsman
            [('CSK01', 'M001', 1, 'out', 10.0)],  # wickets
            [('CSK', 'MI')]  # teams
        ]

        result = get_batting_stats_by_match('M001')

        assert isinstance(result, list)

    def test_get_wickets_by_match_success(self, mock_db_manager, mock_cursor):
        """Test get_wickets_by_match with data."""
        mock_cursor.fetchall.side_effect = [
            [('M001', 'CSK01', 1, 'bowled', 5.0)],  # wickets
            [('CSK', 'MI')],  # teams
            [('Player1',)],  # name
            [('50',)]  # score
        ]

        result = get_wickets_by_match('M001')

        assert isinstance(result, list)

    def test_get_score_summaries_by_match_success(self, mock_db_manager, mock_cursor):
        """Test get_score_summaries_by_match with data."""
        mock_cursor.fetchall.side_effect = [
            [(1.0, 'M001', 'CSK01', 'CSK02', 'CSK03', 'CSK', 100, 5, None, None, 5.0, None)],  # scores1
            [],  # scores2
            [('Player1',)], [('Player2',)], [('Player3',)]  # names
        ]

        result = get_score_summaries_by_match('M001', 'CSK', 'MI')

        assert isinstance(result, dict)

    def test_get_score_by_over_success(self, mock_db_manager, mock_cursor):
        """Test get_score_by_over with data."""
        mock_cursor.fetchall.side_effect = [
            [(1.0, 'M001', 'CSK01', 'CSK02', 'CSK03', 'CSK', 100, 5, None, None, 5.0, None)],  # score
            [('Player1',)], [('Player2',)], [('Player3',)]  # names
        ]

        result = get_score_by_over('M001', 'CSK', '1.0')

        assert isinstance(result, list)

    def test_get_team_names_by_match_id_success(self, mock_db_manager, mock_cursor):
        """Test get_team_names_by_match_id with data."""
        mock_cursor.fetchall.return_value = [('CSK', 'MI')]

        result = get_team_names_by_match_id('M001')

        assert result == ('CSK', 'MI')

    def test_get_top_players_stats_success(self, mock_db_manager, mock_cursor):
        """Test get_top_players_stats with data."""
        mock_cursor.fetchall.return_value = [('Player1',)]

        result = get_top_players_stats()

        assert isinstance(result, dict)
        assert 'orange_cap' in result

    def test_get_final_score_summary_success(self, mock_db_manager, mock_cursor):
        """Test get_final_score_summary with data."""
        mock_cursor.fetchall.side_effect = [
            [(20.0, 100, 'CSK', 'M001')],  # score data
            [],  # no more data
            [],  # no more data
            [('Player1',)], [('Player2',)], [('Player3',)]  # names
        ]

        result = get_final_score_summary('M001', 'CSK', 'MI')

        assert isinstance(result, dict)