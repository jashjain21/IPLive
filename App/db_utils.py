from flask import g, current_app
from App.databases import DatabaseManager

def get_db_manager():
    if 'db_manager' not in g:
        g.db_manager = DatabaseManager(current_app.config['DB_CONFIG'])
    return g.db_manager