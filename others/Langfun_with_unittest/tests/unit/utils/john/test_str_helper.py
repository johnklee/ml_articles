import unittest
from utils.john.str_helper import to_upper


class TestToUpper(unittest.TestCase):
    def test_to_upper_empty(self):
        self.assertEqual(to_upper(""), "")

    def test_to_upper_single_char(self):
        self.assertEqual(to_upper("a"), "A")

    def test_to_upper_multiple_chars(self):
        self.assertEqual(to_upper("abc"), "ABC")

    def test_to_upper_mixed_case(self):
        self.assertEqual(to_upper("aBc"), "ABC")

    def test_to_upper_with_space(self):
        self.assertEqual(to_upper("a b"), "A B")

    def test_to_upper_with_special_chars(self):
        self.assertEqual(to_upper("!@#$"), "!@#$")

    def test_to_upper_already_upper(self):
        self.assertEqual(to_upper("ABC"), "ABC")

    def test_to_upper_non_ascii(self):
        self.assertEqual(to_upper("你好"), "你好") # Non-ASCII characters should remain unchanged

