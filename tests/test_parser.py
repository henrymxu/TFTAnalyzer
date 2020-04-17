import unittest

from tft import window, game, parser, board, debugger

TestWindowName = "TFTAnalyzer Test Window"
Test1080PDefault = "/Users/henry/Downloads/TFT Screenshots/Screenshot_10.png"
Test1440PDefault = "/Users/henry/Downloads/TFT Screenshots/Screenshot_11.png"


class TestParser(unittest.TestCase):

    def setUp(self):
        self.debug = debugger.Debugger()
        self.debug.enable_parse_players()
        self.subject = parser.Parser(self.debug)

    def test_players_1080p(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/players_1080P_1.png")
        players = game.retrieve_player_list(gameWindow, gameBoard, self.subject)
        self.assertEqual(len(players), 8)
        for player in players:
            self.assertNotEqual("", player)

    def test_players_1440p(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/players_2560P_1.png")
        players = game.retrieve_player_list(gameWindow, gameBoard, self.subject)
        self.assertEqual(len(players), 8)
        for player in players:
            self.assertNotEqual("", player)

    def test_healthbars_1080p(self):
        gameWindow, gameBoard = initialize_screenshot(
            Test1080PDefault)
        img = gameWindow.captureWindow()
        top_to_bottom = board.crop_healthbar(img, gameBoard, 0)
        bottom_to_top = board.crop_healthbar(img, gameBoard, 1)
        healthbars = self.subject.parse_healthbars(top_to_bottom, bottom_to_top)
        print(healthbars)

    def test_healthbars_1440p(self):
        gameWindow, gameBoard = initialize_screenshot(
            Test1440PDefault)
        img = gameWindow.captureWindow()
        top_to_bottom = board.crop_healthbar(img, gameBoard, 0)
        bottom_to_top = board.crop_healthbar(img, gameBoard, 1)
        healthbars = self.subject.parse_healthbars(top_to_bottom, bottom_to_top)
        print(healthbars)

    def test_level_1080p(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        level = self.subject.parse_level(board.crop_level(img, gameBoard))
        self.assertEqual(level, "6")

    def test_level_1440p(self):
        gameWindow, gameBoard = initialize_screenshot(Test1440PDefault)
        img = gameWindow.captureWindow()
        level = self.subject.parse_level(board.crop_level(img, gameBoard))
        self.assertEqual(level, "8")

    def test_stage_1080p(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        stage = self.subject.parse_stage(board.crop_stage(img, gameBoard))
        self.assertEqual(stage, "4-5")

    def test_stage_1440p(self):
        gameWindow, gameBoard = initialize_screenshot(Test1440PDefault)
        img = gameWindow.captureWindow()
        stage = self.subject.parse_stage(board.crop_stage(img, gameBoard))
        self.assertEqual(stage, "5-5")

    def test_shop_1080p(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        shop = self.subject.parse_shop(board.crop_shop(img, gameBoard))
        self.assertEqual(shop, ['Blitzerank', 'Graves', 'Ziggs', 'Zoe', 'Vi'])

    def test_shop_1440p(self):
        gameWindow, gameBoard = initialize_screenshot(Test1440PDefault)
        img = gameWindow.captureWindow()
        shop = self.subject.parse_shop(board.crop_shop(img, gameBoard))
        self.assertEqual(shop, ['Rakan', '', 'Yasuo', 'Vel’iKoz', 'Sona'])

    def test_gold_1080p(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefault)
        img = gameWindow.captureWindow()
        gold = self.subject.parse_gold(board.crop_gold(img, gameBoard))
        self.assertEqual(gold, "50")

    def test_gold_1440p(self):
        gameWindow, gameBoard = initialize_screenshot(Test1440PDefault)
        img = gameWindow.captureWindow()
        gold = self.subject.parse_gold(board.crop_gold(img, gameBoard))
        self.assertEqual(gold, "20")


def initialize_screenshot(file_name):
    gameWindow = window.StaticImageWindow(TestWindowName, file_name)
    gameWindow.showWindow()
    gameBoard = game.initialize_game_board(gameWindow)
    return gameWindow, gameBoard


if __name__ == '__main__':
    unittest.main()
