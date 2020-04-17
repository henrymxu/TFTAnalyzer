import unittest

from tft import utils


class TestUtils(unittest.TestCase):
    def test_assert_stage_regex(self):
        self.assertTrue(utils.assert_stage_string_format("2-1"))
        self.assertTrue(utils.assert_stage_string_format("1-3"))
        self.assertFalse(utils.assert_stage_string_format("0-5"))
        self.assertFalse(utils.assert_stage_string_format("1-G"))
        self.assertFalse(utils.assert_stage_string_format("10-5"))

    def test_convert_string_to_integer(self):
        self.assertEqual("8", 8)
        self.assertTrue("asdf", -1)


if __name__ == '__main__':
    unittest.main()
