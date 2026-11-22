import unittest
from routes.stremio import _parse

class StremioIdTests(unittest.TestCase):
    def test_movie(self):
        self.assertEqual(_parse("movie","tt1234567"),("tt1234567",None,None))
    def test_episode(self):
        self.assertEqual(_parse("series","tt1234567:2:10"),("tt1234567",2,10))
    def test_reject_wrong_type_or_id(self):
        self.assertIsNone(_parse("movie","tt1234567:1:2"))
        self.assertIsNone(_parse("series","tt1234567"))
        self.assertIsNone(_parse("other","tt1234567"))

if __name__=="__main__":
    unittest.main()
