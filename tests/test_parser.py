import unittest

from tests import initialize_screenshot
from tft import game, parser, board, debugger, utils, tracker

TestFile = "parser_test_data.json"
Test1080PDefault = "/Users/henry/Downloads/TFT Screenshots/board_1080_2.png"
Test1440PDefault = "/Users/henry/Downloads/TFT Screenshots/board_1440_2.png"


class TestParser(unittest.TestCase):

    def setUp(self):
        self.debug = debugger.Debugger()
        self.debug.enable_parse_players()
        self.subject = parser.Parser(self.debug)
        self.unit_lookup = tracker.initialize_unit_lookup_table()

    def test_players(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/players_1080_2.png")
        players = game.retrieve_player_list(gameWindow, gameBoard, self.subject)
        self.assertEqual(len(players), 8)
        for player in players:
            self.assertNotEqual("", player)

    def test_healthbars_1440p(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        top_to_bottom = board.crop_healthbar(img, gameBoard, 0)
        bottom_to_top = board.crop_healthbar(img, gameBoard, 1)
        healthbars = self.subject.parse_healthbars(top_to_bottom, bottom_to_top)
        print(healthbars)

    def test_level(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        level = self.subject.parse_level(board.crop_level(img, gameBoard))
        self.assertEqual(level, 6)

    def test_stage(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        stage = self.subject.parse_stage(board.crop_stage(img, gameBoard))
        self.assertEqual(stage, "4-5")

    def test_stage_early(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/board_1080P_1.png")
        img = gameWindow.captureWindow()
        stage = self.subject.parse_stage(board.crop_stage_early(img, gameBoard))
        self.assertEqual(stage, "1-3")

    def test_shop(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        shop = self.subject.parse_shop(board.crop_shop(img, gameBoard))
        self.assertEqual(shop, ['Blitzerank', 'Graves', 'Ziggs', 'Zoe', 'Vi'])

    def test_gold(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        gold = self.subject.parse_gold(board.crop_gold(img, gameBoard))
        self.assertEqual(gold, 50)

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
        shop = testcase.subject.parse_shop(board.crop_shop(img, gameBoard))
        shop = [utils.find_matching_string_in_list(unit, testcase.unit_lookup) for unit in shop]
        print("Asserting shop: {}".format(shop))
        testcase.assertEqual(data["shop"], shop)
    if "level" in data:
        level = testcase.subject.parse_level(board.crop_level(img, gameBoard))
        print("Asserting level: {}".format(level))
        testcase.assertEqual(data["level"], level)
    if "stage" in data:
        stage = testcase.subject.parse_stage(board.crop_stage(img, gameBoard))
        if not utils.assert_stage_string_format(stage):
            stage = testcase.subject.parse_stage(board.crop_stage_early(img, gameBoard))
        print("Asserting stage: {}".format(stage))
        testcase.assertEqual(data["stage"], stage)
    if "gold" in data:
        gold = testcase.subject.parse_gold(board.crop_gold(img, gameBoard))
        print("Asserting gold: {}".format(gold))
        testcase.assertEqual(data["gold"], gold)
    if "players" in data:
        if isinstance(data["players"], list):
            players = testcase.subject.parse_players(board.crop_players(img, gameBoard))
            print("Asserting players: {}".format(players))
            for player in players:
                if player == "You":
                    continue
                res = utils.find_matching_string_in_list(player, data["players"])
                testcase.assertIsNot(res, "", "Unable to find match for {}".format(player))
        elif isinstance(data["players"], dict):
            top_to_bottom = board.crop_healthbar(img, gameBoard, 0)
            bottom_to_top = board.crop_healthbar(img, gameBoard, 1)
            healthbars = testcase.subject.parse_healthbars(top_to_bottom, bottom_to_top)
            print("Asserting healthbars: {}".format(healthbars))
            player_names = data["players"].keys()
            blank_count = 0
            for healthbar in healthbars:
                res = utils.find_matching_string_in_list(healthbar[0], player_names)
                if res == "":
                    blank_count += 1
                else:
                    testcase.assertEqual(healthbar[1], data["players"][res])
            testcase.assertLess(blank_count, 2)


if __name__ == '__main__':
    unittest.main()
