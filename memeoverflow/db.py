import sqlite3


class MemeDatabase:
    """
    Meme database interface (sqlite)

    :param str site:
        The name of the StackExchange site as an identifier (used as the table
        name)

    :param str db_path:
        Path to the sqlite database file
    """
    def __init__(self, site, db_path):
        if not isinstance(site, str) or len(site) == 0:
            raise TypeError('site must be a non-empty string')
        if not isinstance(db_path, str) or len(db_path) == 0:
            raise TypeError('db_path must be a non-empty string')
        self.site = site
        self.conn = sqlite3.connect(db_path)
        cursor = self.conn.cursor()
        cursor.execute(f'create table if not exists {site} (question_id int unique)')
        cursor.close()

    def __repr__(self):
        return f"<MemeDatabase object for site {self.site}>"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def insert_question(self, id):
        "Insert a question ID"
        cursor = self.conn.cursor()
        cursor.execute(f'insert into {self.site} values (?)', (id, ))
        self.conn.commit()
        cursor.close()

    def question_is_known(self, id):
        """
        Return True if the provided question ID is already in the database,
        otherwise return False
        """
        cursor = self.conn.cursor()
        cursor.execute(f'select 1 from {self.site} where question_id = ?', (id, ))
        result = bool(cursor.fetchone())
        cursor.close()
        return result
