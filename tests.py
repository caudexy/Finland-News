import unittest
from bot import titleEditor
from bot import linkEditor

# Simple unitest template to get testing started.
class TestYle(unittest.TestCase):
    """
    """
    def test_titleEditor(self):
        """
        Tests if titleEditor() functions as intended.
        """
        original_title = "-"
        escaped_title = r"\-"
        self.assertEqual(titleEditor(original_title), escaped_title)

    def test_linkEditor(self):
        """
        Tests if linkEditor() functions as intended.
        """
        original = "https://yle.fi/uutiset/osasto/news/trio_hailed_as_heroes_for_alerting_residents_to_apartment_building_fire/12039661?origin=rss"
        result = "https://t.me/iv?url=https%3A%2F%2Fyle.fi%2Fuutiset%2Fosasto%2Fnews%2Ftrio_hailed_as_heroes_for_alerting_residents_to_apartment_building_fire%2F12039661?origin=rss&rhash=04f872b445da2a"
        yle_newsfeed_eng = "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_NEWS"
        
        self.assertEqual(linkEditor(original,yle_newsfeed_eng), result)

if __name__ == "__main__":
    unittest.main()