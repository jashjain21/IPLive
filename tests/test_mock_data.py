import pytest
from App.mock_data import MockCricbuzz, mock_live_score


class TestMockCricbuzz:
    def test_matches_returns_list(self):
        """Test that matches() returns a list."""
        c = MockCricbuzz()
        matches = c.matches()
        assert isinstance(matches, list)
        if matches:
            assert 'id' in matches[0]
            assert 'team1' in matches[0]
            assert 'team2' in matches[0]

    def test_scorecard_returns_dict(self):
        """Test that scorecard() returns a dict with expected structure."""
        c = MockCricbuzz()
        scorecard = c.scorecard('M001')
        assert isinstance(scorecard, dict)
        assert 'scorecard' in scorecard
        if scorecard['scorecard']:
            assert 'batcard' in scorecard['scorecard'][0]
            assert 'bowlcard' in scorecard['scorecard'][0]

    def test_scorecard_invalid_id(self):
        """Test scorecard with invalid ID."""
        c = MockCricbuzz()
        scorecard = c.scorecard('INVALID')
        assert isinstance(scorecard, dict)
        # Should handle gracefully

    def test_mock_live_score_structure(self):
        """Test that mock_live_score has expected structure."""
        assert isinstance(mock_live_score, dict)
        expected_keys = ['runs', 'wickets', 'crr', 'req_runs', 'rrr', 'bat1', 'bat2', 'run1', 'run2', 'bowl', 'bowl_wick', 'bowl_run', 'team', 'over_ball', 'ball_faced_1', 'ball_faced_2']
        for key in expected_keys:
            assert key in mock_live_score