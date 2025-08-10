import unittest
from utils.john.str_helper import to_upper


class TestToUpper(unittest.TestCase):
  def test_to_upper_empty(self):
    self.assertEqual(to_upper(""), "")

  def test_to_upper_single_char(self):
    self.assertEqual(to_upper("a"), "A")

  def test_to_upper_mixed_case(self):
    self.assertEqual(to_upper("aBcDe"), "ABCDE")

  def test_to_upper_with_space(self):
    self.assertEqual(to_upper("abc def"), "ABC DEF")

  def test_to_upper_with_number(self):
    self.assertEqual(to_upper("abc123def"), "ABC123DEF")

  def test_to_upper_with_special_chars(self):
    self.assertEqual(to_upper("!@#%^"), "!@#%^")

  def test_to_upper_with_unicode(self):
    self.assertEqual(to_upper("你好世界"), "你好世界")

  def test_to_upper_None_input(self):
    with self.assertRaises(AttributeError):
      to_upper(None)

  def test_to_upper_int_no_upper(self):
    with self.assertRaises(ValueError):
      to_upper(123)
