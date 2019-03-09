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
        cursor.execute(f"create table if not exists {site} (question_id int unique)")
        cursor.execute(f"create table if not exists memes (meme_id int unique, meme_name text, blacklisted bool, include_random bool)")
        cursor.close()

    def __repr__(self):
        return f"<MemeDatabase object for site {self.site}>"

    def insert_memes(self, memes):
        """
        Insert memes
        """
        cursor = self.conn.cursor()
        try:
            cursor.executemany("insert or ignore into memes values (?, ?, 0, 1)", memes)
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
        cursor.close()

    def select_random_meme(self):
        """
        Select a random meme ID
        """
        cursor = self.conn.cursor()
        cursor.execute(f"select meme_id from memes where include_random and not blacklisted order by random() limit 1")
        result = cursor.fetchone()
        cursor.close()
        return result[0]

    def select_meme(self, id):
        """
        Look up a specific meme by ID
        """
        cursor = self.conn.cursor()
        cursor.execute(f"select meme_name from memes where meme_id = ?", (id, ))
        result = cursor.fetchone()
        cursor.close()
        return result[0]

    def search_for_meme(self, search):
        """
        Look up a specific meme by searching
        """
        cursor = self.conn.cursor()
        cursor.execute(f"select * from memes where lower(meme_name) like ?", (f'%{search}%', ))
        results = cursor.fetchall()
        cursor.close()
        return results

    def blacklist_meme(self, id):
        """
        Blacklist a meme ID
        """
        cursor = self.conn.cursor()
        cursor.execute(f"update memes set blacklisted = 1 where meme_id = ?", (id, ))
        self.conn.commit()
        cursor.close()

    def insert_question(self, id):
        """
        Insert a question ID
        """
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
        cursor.execute(f"select 1 from {self.site} where question_id = ?", (id, ))
        result = bool(cursor.fetchone())
        cursor.close()
        return result
