import unittest

from tft import window, image_utils, game, parser, board

TestWindowName = "TFTAnalyzer Test Window"


class TestParserPlayers(unittest.TestCase):
    def test_players_1080p(self):
        self.test_players("/Users/henry/Downloads/TFT Screenshots/Screenshot_12.png")

    def test_players_1440p(self):
        self.test_players("/Users/henry/Downloads/TFT Screenshots/Screenshot_13.png")

    def test_players(self, file):
        gameWindow, gameBoard = initialize_screenshot(file)
        players = game.retrieve_player_list(gameWindow, gameBoard)
        self.assertEqual(len(players), 8)
        for player in players:
            self.assertNotEqual("", player)


class TestParserHealthbars(unittest.TestCase):
    def test_healthbars(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/Screenshot_11.png")
        img = gameWindow.captureWindow()
        top_to_bottom = board.crop_healthbar(img, gameBoard, 0)
        bottom_to_top = board.crop_healthbar(img, gameBoard, 1)
        healthbars = parser.parse_healthbars(top_to_bottom, bottom_to_top)
        print(healthbars)


class TestParserLevel(unittest.TestCase):
    def test_level_1080p(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/Screenshot_10.png")
        img = gameWindow.captureWindow()
        level = parser.parse_level(board.crop_level(img, gameBoard))
        self.assertEqual(level, "6")

    def test_level_1440p(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/Screenshot_11.png")
        img = gameWindow.captureWindow()
        level = parser.parse_level(board.crop_level(img, gameBoard))
        self.assertEqual(level, "8")


class TestParserStage(unittest.TestCase):
    def test_level_1080p(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/Screenshot_10.png")
        img = gameWindow.captureWindow()
        stage = parser.parse_stage(board.crop_stage(img, gameBoard))
        self.assertEqual(stage, "4-5")

    def test_level_1440p(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/Screenshot_11.png")
        img = gameWindow.captureWindow()
        stage = parser.parse_stage(board.crop_stage(img, gameBoard))
        self.assertEqual(stage, "5-5")


class TestParserShop(unittest.TestCase):
    def test_level_1080p(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/Screenshot_10.png")
        img = gameWindow.captureWindow()
        shop = parser.parse_shop(board.crop_shop(img, gameBoard))
        self.assertEqual(shop, ['Blitzerank', 'Graves', 'Ziggs', 'Zoe', 'Vi'])

    def test_level_1440p(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/Screenshot_11.png")
        img = gameWindow.captureWindow()
        shop = parser.parse_shop(board.crop_shop(img, gameBoard))
        self.assertEqual(shop, ['Rakan', '', 'Yasuo', 'Vel’iKoz', 'Sona'])


class TestParserGold(unittest.TestCase):
    def test_level_1080p(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/Screenshot_10.png")
        img = gameWindow.captureWindow()
        gold = parser.parse_gold(board.crop_gold(img, gameBoard))
        self.assertEqual(gold, "50")

    def test_level_1440p(self):
        gameWindow, gameBoard = initialize_screenshot("/Users/henry/Downloads/TFT Screenshots/Screenshot_11.png")
        img = gameWindow.captureWindow()
        gold = parser.parse_gold(board.crop_gold(img, gameBoard))
        self.assertEqual(gold, "20")


def initialize_screenshot(file_name):
    gameWindow = window.StaticImageWindow(TestWindowName, file_name)
    image = gameWindow.captureWindow()
    image_utils.show_image(image, TestWindowName)
    gameBoard = game.initialize_game_board(gameWindow)
    return gameWindow, gameBoard


if __name__ == '__main__':
    unittest.main()
