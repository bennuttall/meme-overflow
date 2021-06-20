import pytest
import os

from memeoverflow import MemeDatabase

db_path = 'test_memes.db'


def teardown_db(db_path):
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass

def test_database_bad_connect():
    teardown_db(db_path)
    with pytest.raises(TypeError):
        MemeDatabase()

def test_database_good_connect():
    teardown_db(db_path)
    with MemeDatabase('foo', db_path) as db:
        assert repr(db).startswith("<MemeDatabase")
        assert repr(db).endswith("site='foo'>")
    teardown_db(db_path)

def test_database_init():
    teardown_db(db_path)
    with MemeDatabase('foo', db_path) as db:
        cursor = db.conn.cursor()
        cursor.execute(f"select count(*) from foo")
        result = cursor.fetchone()
        assert result[0] == 0
        cursor.close()
        assert not db.question_is_known(123)
    teardown_db(db_path)

def test_database_insert():
    teardown_db(db_path)
    with MemeDatabase('foo', db_path) as db:
        db.insert_question(123)
        cursor = db.conn.cursor()
        cursor.execute(f"select count(*) from foo")
        result = cursor.fetchone()
        assert result[0] == 1
        cursor.execute(f"select question_id from foo")
        result = cursor.fetchone()
        assert result[0] == 123
        cursor.close()
        assert db.question_is_known(123)
    teardown_db(db_path)

def test_database_persistence():
    teardown_db(db_path)
    with MemeDatabase('foo', db_path) as db:
        db.insert_question(123)
        assert db.question_is_known(123)
    with MemeDatabase('foo', db_path) as db:
        assert db.question_is_known(123)
    teardown_db(db_path)

def test_database_multi_insert():
    teardown_db(db_path)
    ids = range(100, 200)
    with MemeDatabase('foo', db_path) as db:
        for id in ids:
            assert not db.question_is_known(id)
            db.insert_question(id)
            assert db.question_is_known(id)
    teardown_db(db_path)
