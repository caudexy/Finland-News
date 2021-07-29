import unittest
from bot import titleEditor

# Simple unitest template to get testing started.
class TestYle(unittest.TestCase):
    """
    """
    def test_titleEditor(self):
        """
        Tests if titleEditor() function works correctly
        """
        original_title = "-"
        escaped_title = r"\-"
        self.assertEqual(titleEditor(original_title), escaped_title)

if __name__ == "__main__":
    unittest.main()