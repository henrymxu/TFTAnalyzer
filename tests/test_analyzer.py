import unittest

from tft import analyzer, utils


class TestAnalyzer(unittest.TestCase):
    def test_cleanup(self):
        dict = utils.open_json_file("test/1588121154.json")[0]
        analyzer.clean_up_json(dict)


if __name__ == '__main__':
    unittest.main()
