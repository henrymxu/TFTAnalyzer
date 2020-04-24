import unittest

from tft import utils


class TestUtils(unittest.TestCase):
    def test_assert_stage_regex(self):
        self.assertTrue(utils.assert_stage_string_format("2-1"))
        self.assertTrue(utils.assert_stage_string_format("1-3"))
        self.assertFalse(utils.assert_stage_string_format("0-5"))
        self.assertFalse(utils.assert_stage_string_format("1-G"))
        self.assertFalse(utils.assert_stage_string_format("10-5"))

    def test_parse_stage_round(self):
        self.assertEqual(utils.parse_stage_round("2-1"), (2, 1))
        self.assertEqual(utils.parse_stage_round("4-5"), (4, 5))
        self.assertEqual(utils.parse_stage_round("1-1"), (1, 1))
        self.assertEqual(utils.parse_stage_round("5-7"), (5, 7))
        self.assertEqual(utils.parse_stage_round("1-G"), (0, 0))

    def test_convert_string_to_integer(self):
        self.assertEqual(utils.convert_string_to_integer("8"), 8)
        self.assertEqual(utils.convert_string_to_integer("asdf"), -1)
        self.assertEqual(utils.convert_string_to_integer("0"), 0)

    def test_clean_string(self):
        self.assertEqual(utils.clean_string("[]~test*&^"), "test")


if __name__ == '__main__':
    unittest.main()
