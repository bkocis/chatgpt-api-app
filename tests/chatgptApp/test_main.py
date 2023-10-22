import unittest
import sqlite3
from chatgptApp.main import on_clear_click
from unittest.mock import mock_open, patch
from chatgptApp.main import load_style
from chatgptApp.main import insert_into_db


class TestOnClearClick(unittest.TestCase):
    def test_on_clear_click(self):
        expected_output = ("", [], [])
        self.assertEqual(on_clear_click(), expected_output)


def test_load_style():
    m = mock_open(read_data="Test content")
    with patch('builtins.open', m):
        assert load_style() == ("Test content", "Test content")


def test_insert_into_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    c = conn.cursor()
    c.execute("CREATE TABLE test_table (question text, answer text)")

    insert_into_db(conn, "test_table", "Hello", "World")

    c.execute("SELECT * FROM test_table")
    assert c.fetchone() == ("Hello", "World")
