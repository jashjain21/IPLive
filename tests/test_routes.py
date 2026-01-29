import pytest
from unittest.mock import patch


class TestRoutes:
    def test_index_route(self, client, mock_db_manager):
        """Test the index route."""
        with patch('App.app.do_it', return_value=('M001', {})), \
             patch('App.mock_data.MockCricbuzz.scorecard', return_value={'scorecard': []}), \
             patch('App.app.get_bowling_stats_by_match', return_value=[]), \
             patch('App.app.get_batting_stats_by_match', return_value=[]), \
             patch('App.app.get_wickets_by_match', return_value=[]):
            response = client.get('/')
            assert response.status_code == 200
            assert b'IPLive' in response.data

    def test_archive_route(self, client, mock_db_manager):
        """Test the archive route."""
        with patch('App.app.get_all_matches', return_value=[]):
            response = client.get('/archive/')
            assert response.status_code == 200
            assert b'Archives' in response.data

    def test_match_route(self, client, mock_db_manager):
        """Test the match details route."""
        with patch('App.app.get_batting_stats_by_match', return_value=['CSK', []]), \
             patch('App.app.get_bowling_stats_by_match', return_value=[]), \
             patch('App.app.get_wickets_by_match', return_value=[]), \
             patch('App.app.get_final_score_summary', return_value={}):
            response = client.get('/archive/match?id=M001')
            assert response.status_code == 200

    def test_player_search_route_get(self, client):
        """Test the player search route GET."""
        response = client.get('/playerstats/')
        assert response.status_code == 200
        assert b'Player Statistics' in response.data

    def test_player_search_route_post(self, client, mock_db_manager):
        """Test the player search route POST."""
        with patch('App.app.search_players', return_value=[]):
            response = client.post('/playerstats/', data={'plyr': 'Test', 'team': 'CSK'})
            assert response.status_code == 200

    def test_player_details_route(self, client, mock_db_manager):
        """Test the individual player route."""
        with patch('App.app.get_player_by_id', return_value=None):
            response = client.get('/playerstats/player?id=CSK01')
            assert response.status_code == 200

    def test_score_route_get(self, client, mock_db_manager):
        """Test the score route GET."""
        with patch('App.app.get_team_names_by_match_id', return_value=('CSK', 'MI')), \
             patch('App.app.get_score_summaries_by_match', return_value={}):
            response = client.get('/archive/score?id=M001')
            assert response.status_code == 200

    def test_score_route_post(self, client, mock_db_manager):
        """Test the score route POST."""
        with patch('App.app.get_team_names_by_match_id', return_value=('CSK', 'MI')), \
             patch('App.app.get_score_summaries_by_match', return_value={}), \
             patch('App.app.get_score_by_over', return_value=[]):
            response = client.post('/archive/score?id=M001', data={'over': '1.0', 'team': 'CSK'})
            assert response.status_code == 200

    def test_404_route(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        assert b'Page not found' in response.data

    def test_internal_error(self, client):
        """Test 500 error handling."""
        with patch('App.app.get_all_matches', side_effect=Exception("Test error")):
            response = client.get('/archive/')
            assert response.status_code == 500