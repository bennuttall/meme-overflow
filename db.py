import sqlite3


class MemeDatabase:
    def __init__(self, database):
        self.database = database
        self.conn = sqlite3.connect('memes.db')
        cursor = self.conn.cursor()
        cursor.execute(f"create table if not exists {database} (url text)")
        cursor.close()

    def insert(self, url):
        cursor = self.conn.cursor()
        cursor.execute(f"insert into {self.database} values (?)", (url, ))
        self.conn.commit()
        cursor.close()

    def select(self, url):
        cursor = self.conn.cursor()
        cursor.execute(f"select 1 from {self.database} where url = ?", (url, ))
        result = bool(cursor.fetchone())
        cursor.close()
        return result
