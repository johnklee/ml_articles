import unittest
from utils.john.str_helper import to_upper

class TestToUpper(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(to_upper(""), "")

    def test_lower_case_string(self):
        self.assertEqual(to_upper("hello"), "HELLO")

    def test_mixed_case_string(self):
        self.assertEqual(to_upper("hELLo"), "HELLO")

    def test_already_upper_case_string(self):
        self.assertEqual(to_upper("HELLO"), "HELLO")

    def test_non_ascii_characters(self):
      self.assertEqual(to_upper("你好"), "你好") # Non-ASCII should remain unchanged

    def test_numeric_input(self):
        with self.assertRaises(AttributeError): # Numbers do not have upper() methods
            to_upper(123)

    def test_none_input(self):
        with self.assertRaises(AttributeError): # Check for None input
            to_upper(None)

if __name__ == "__main__":
    unittest.main()