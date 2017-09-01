import unittest
from dash-fda.example import add


class TestExample(unittest.TestCase):

    def test_add_one_and_two_gives_three(self):
        self.assertEqual(add(1, 2), 3)

if __name__ == '__main__':
    unittest.main()
