import unittest

from tests import initialize_screenshot
from tft import game, board, utils, tracker, parser, debugger

TestFile = "parser_test_data.json"
Test1080PDefault = "/Users/henry/Downloads/TFT Screenshots/board_1080_1.png"
Test1440PDefault = "/Users/henry/Downloads/TFT Screenshots/board_1440_1.png"


class TestParser(unittest.TestCase):

    def setUp(self):
        self.unit_lookup = tracker.initialize_unit_lookup_table()
        self.debug = debugger.Debugger()

    def test_players(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/players_1080_2.png")
        players = game.retrieve_player_list(gameWindow, gameBoard)
        self.assertEqual(len(players), 8)
        for player in players:
            self.assertNotEqual("", player)

    def test_healthbars(self):
        gameWindow, gameBoard = initialize_screenshot(Test1440PDefault)
        img = gameWindow.captureWindow()
        cropped_circles = board.crop_healthbar_circles(img, gameBoard)
        result = parser.parse_healthbar_circles(cropped_circles, self.debug)
        values = board.crop_healthbars(img, gameBoard, result)
        print(parser.parse_healthbars(values, debug=self.debug))

    def test_healthbars_legacy(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        top_to_bottom = board.crop_healthbars_legacy(img, gameBoard, 0)
        bottom_to_top = board.crop_healthbars_legacy(img, gameBoard, 1)
        healthbars = parser.parse_healthbars_legacy(top_to_bottom, bottom_to_top)
        print(healthbars)

    def test_level(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        level = parser.parse_level(board.crop_level(img, gameBoard))
        self.assertEqual(level, 6)

    def test_stage(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        stage = parser.parse_stage(board.crop_stage(img, gameBoard))
        self.assertEqual(stage, "4-5")

    def test_stage_early(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/board_1080_1.png")
        img = gameWindow.captureWindow()
        stage = parser.parse_stage(board.crop_stage_early(img, gameBoard))
        self.assertEqual(stage, "1-3")

    def test_shop(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        shop = parser.parse_shop(board.crop_shop(img, gameBoard))
        self.assertEqual(shop, ['Blitzcrank', 'Graves', 'Ziggs', 'Zoe', 'Vi'])

    def test_gold(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        gold = parser.parse_gold(board.crop_gold(img, gameBoard))
        self.assertEqual(gold, 50)

    def test_timer(self):
        gameWindow, gameBoard = initialize_screenshot(Test1440PDefault)
        img = gameWindow.captureWindow()
        timer = parser.parse_timer(board.crop_timer_early(img, gameBoard))
        print(timer)

    def test_parser_complete_1080p(self):
        initialize_complete_test(self, "players", "1080")
        initialize_complete_test(self, "board", "1080")

    def test_parser_complete_1440p(self):
        initialize_complete_test(self, "players", "1440")
        initialize_complete_test(self, "board", "1440")


def initialize_complete_test(testcase, type, resolution):
    tests = utils.open_json_file("tests/parser_test_data.json")[type][resolution]
    for test in tests:
        file = "/Users/henry/Downloads/TFT Screenshots/{}".format(test["file_name"])
        print("Testing Screenshot: {}".format(file))
        gameWindow, gameBoard = initialize_screenshot(file)
        img = gameWindow.captureWindow()
        run_complete_parser_test(testcase, img, test, gameBoard)


def run_complete_parser_test(testcase, img, data, gameBoard):
    if "shop" in data:
        shop = parser.parse_shop(board.crop_shop(img, gameBoard), testcase.debug)
        shop = [utils.find_matching_string_in_list(unit, testcase.unit_lookup) for unit in shop]
        print("Asserting shop: {}".format(shop))
        testcase.assertEqual(data["shop"], shop)
    if "level" in data:
        level = parser.parse_level(board.crop_level(img, gameBoard), testcase.debug)
        print("Asserting level: {}".format(level))
        testcase.assertEqual(data["level"], level)
    if "stage" in data:
        stage = parser.parse_stage(board.crop_stage(img, gameBoard), testcase.debug)
        if not utils.assert_stage_string_format(stage):
            stage = parser.parse_stage(board.crop_stage_early(img, gameBoard), testcase.debug)
        print("Asserting stage: {}".format(stage))
        testcase.assertEqual(data["stage"], stage)
    if "timer" in data:
        timer = parser.parse_timer(board.crop_timer(img, gameBoard), testcase.debug)
        if timer == - 1:
            timer = parser.parse_timer(board.crop_timer_early(img, gameBoard), testcase.debug)
        print("Asserting timer: {}".format(timer))
        testcase.assertEqual(data["timer"], timer)
    if "gold" in data:
        gold = parser.parse_gold(board.crop_gold(img, gameBoard), testcase.debug)
        print("Asserting gold: {}".format(gold))
        testcase.assertEqual(data["gold"], gold)
    if "players" in data:
        if isinstance(data["players"], list):
            players = parser.parse_players(board.crop_players(img, gameBoard), testcase.debug)
            print("Asserting players: {}".format(players))
            for player in players:
                if player == "You":
                    continue
                res = utils.find_matching_string_in_list(player, data["players"])
                testcase.assertIsNot(res, "", "Unable to find match for {}".format(player))
        elif isinstance(data["players"], dict):
            cropped_circles = board.crop_healthbar_circles(img, gameBoard)
            result = parser.parse_healthbar_circles(cropped_circles, testcase.debug)
            cropped_healthbars = board.crop_healthbars(img, gameBoard, result)
            healthbars = parser.parse_healthbars(cropped_healthbars, testcase.debug)
            print("Asserting healthbars: {}".format(healthbars))
            player_names = data["players"].keys()
            for healthbar in healthbars:
                res = utils.find_matching_string_in_list(healthbar[0], player_names)
                health = healthbar[1]
                if res == "" and healthbar[0].isdigit(): # Own HP Testcase
                    health = utils.convert_string_to_integer(healthbar[0])
                testcase.assertEqual(health, data["players"][res])


if __name__ == '__main__':
    unittest.main()
