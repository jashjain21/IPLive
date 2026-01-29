from mysql.connector import pooling

class DatabaseManager:
    def __init__(self, config, pool_size=5):
        self.pool = pooling.MySQLConnectionPool(
            pool_name="iplive_pool",
            pool_size=pool_size,
            **config
        )

    def get_connection(self):
        """Get a connection from the pool."""
        return self.pool.get_connection()

    def __enter__(self):
        """Enter context manager, get a connection."""
        self.conn = self.get_connection()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager, close the connection."""
        if self.conn:
            self.conn.close()