import unittest


@unittest.skip("Dumb test")
class TestCaseSoIDEIsHappy(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)  # add assertion here


if __name__ == '__main__':
    unittest.defaultTestLoader = unittest.TestLoader()
    unittest.defaultTestLoader.discover("GameFiles/UnitTests", "*.py")
    unittest.main()
