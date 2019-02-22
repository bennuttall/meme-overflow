import sqlite3


class MemeDatabase:
    """
    Meme database interface

    :type site: str
    :param site:
        The name of the StackExchange site as an identifier (used as the table
        name)
    """
    def __init__(self, site):
        self.site = site
        self.conn = sqlite3.connect('memes.db')
        cursor = self.conn.cursor()
        cursor.execute(f"create table if not exists {site} (url text)")
        cursor.close()

    def insert(self, url):
        """
        Insert the url provided into the database
        """
        cursor = self.conn.cursor()
        cursor.execute(f"insert into {self.site} values (?)", (url, ))
        self.conn.commit()
        cursor.close()

    def select(self, url):
        """
        Return True if the provided url is already in the database, otherwise
        return False
        """
        cursor = self.conn.cursor()
        cursor.execute(f"select 1 from {self.site} where url = ?", (url, ))
        result = bool(cursor.fetchone())
        cursor.close()
        return result
