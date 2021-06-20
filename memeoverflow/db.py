import sqlite3


class MemeDatabase:
    """
    Wrapper for Meme database interface (sqlite)

    :type site: str
    :param site:
        The name of the StackExchange site as an identifier (used as the table
        name)

    :type db_path: str
    :param db_path: Path to the sqlite database file
    """
    def __init__(self, site, db_path):
        self.site = site
        self.conn = sqlite3.connect(db_path)
        cursor = self.conn.cursor()
        cursor.execute(
            f"create table if not exists {site} (question_id int unique)"
        )
        cursor.close()

    def __repr__(self):
        return f"<MemeDatabase site='{self.site}'>"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def insert_question(self, id):
        "Insert a question ID"
        cursor = self.conn.cursor()
        cursor.execute(f"insert into {self.site} values (?)", (id, ))
        self.conn.commit()
        cursor.close()

    def question_is_known(self, id):
        """
        Return True if the provided question ID is already in the database,
        otherwise return False
        """
        cursor = self.conn.cursor()
        cursor.execute(
            f"select 1 from {self.site} where question_id = ?",
            (id, )
        )
        result = bool(cursor.fetchone())
        cursor.close()
        return result
