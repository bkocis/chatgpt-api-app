import unittest
from main import on_clear_click


class TestOnClearClick(unittest.TestCase):
    def test_on_clear_click(self):
        expected_output = ("", [], [])
        self.assertEqual(on_clear_click(), expected_output)
