import unittest
from utils.my_math import add


class TestAdd(unittest.TestCase):
    def test_positive_integers(self):
        self.assertEqual(add(1, 2), 3)

    def test_negative_integers(self):
        self.assertEqual(add(-1, -2), -3)

    def test_zero_sum(self):
        self.assertEqual(add(0, 0), 0)

    def test_positive_and_negative(self):
        self.assertEqual(add(1, -2), -1)
