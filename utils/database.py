import sqlite3

class Database:
    """
    Manages interactions with a static database for tracking progress.
    """
    def __init__(self, db_uri):
        self.conn = sqlite3.connect(db_uri)
        self.create_table()

    def create_table(self):
        """
        Creates a table for logging progress.
        """
        with self.conn:
            self.conn.execute('''CREATE TABLE IF NOT EXISTS progress (
                                    id INTEGER PRIMARY KEY,
                                    user_id TEXT,
                                    approval_id TEXT,
                                    status TEXT,
                                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    comments TEXT
                                 )''')

    def log_approval(self, user_id, approval_id, timestamp, comments):
        """
        Logs the approval details into the database.
        """
        with self.conn:
            self.conn.execute('''INSERT INTO progress (user_id, approval_id, status, timestamp, comments)
                                 VALUES (?, ?, ?, ?, ?)''', 
                                 (user_id, approval_id, 'approved', timestamp, comments))

    def get_approval(self, approval_id):
        """
        Retrieves the approval details from the database.
        """
        with self.conn:
            cursor = self.conn.execute('''SELECT * FROM progress WHERE approval_id=?''', (approval_id,))
            return cursor.fetchone()
