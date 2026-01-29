import pytest
from unittest.mock import MagicMock, patch
import mysql.connector

@pytest.fixture
def mock_cursor():
    """Mock database cursor."""
    cursor = MagicMock()
    return cursor

@pytest.fixture
def mock_conn(mock_cursor):
    """Mock database connection."""
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    return conn

@pytest.fixture
def mock_db_manager(mock_conn):
    """Mock database manager context manager."""
    with patch('App.repository.get_db_manager') as mock_get_db:
        mock_get_db.return_value.__enter__.return_value = mock_conn
        mock_get_db.return_value.__exit__.return_value = None
        yield mock_get_db

@pytest.fixture
def app():
    """Flask app fixture for testing."""
    from App.app import app as flask_app
    flask_app.config['TESTING'] = True
    flask_app.config['DB_CONFIG'] = {
        'host': 'localhost',
        'user': 'test',
        'password': 'test',
        'database': 'test'
    }
    return flask_app

@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()