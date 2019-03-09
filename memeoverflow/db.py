import sqlite3


class MemeDatabase:
    """
    Meme database interface

    :param str site:
        The name of the StackExchange site as an identifier (used as the table
        name)
    """
    def __init__(self, site):
        self.site = site
        self.conn = sqlite3.connect('memes.db')
        cursor = self.conn.cursor()
        cursor.execute(f"create table if not exists {site} (question_id int)")
        cursor.close()

    def __repr__(self):
        return f"<MemeDatabase object for site {self.site}>"

    def insert(self, id):
        """
        Insert the question ID provided into the database
        """
        cursor = self.conn.cursor()
        cursor.execute(f"insert into {self.site} values (?)", (id, ))
        self.conn.commit()
        cursor.close()

    def select(self, id):
        """
        Return True if the provided question ID is already in the database,
        otherwise return False
        """
        cursor = self.conn.cursor()
        cursor.execute(f"select 1 from {self.site} where question_id = ?", (id, ))
        result = bool(cursor.fetchone())
        cursor.close()
        return result
