import unittest
import sqlite3
from chatgptApp.main import on_clear_click
from chatgptApp.main import insert_into_db


class TestOnClearClick(unittest.TestCase):
    def test_on_clear_click(self):
        expected_output = ("", [], [])
        self.assertEqual(on_clear_click(), expected_output)


def setup_module(module):
    global conn
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.execute("CREATE TABLE chat_session_01 (question text, answer text)")


def teardown_module(module):
    conn.close()


def test_insert_into_db():
    insert_into_db('Hello', 'World')
    c = conn.cursor()
    c.execute("SELECT * FROM chat_session_01")
    assert c.fetchone() == ('Hello', 'World')
