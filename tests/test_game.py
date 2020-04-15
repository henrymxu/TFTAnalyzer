import time
import unittest

from tests import initialize_screenshot
from tft import game, debugger, parser, tracker

TestWindowName = "TFTAnalyzer Test Window"
Test1080PDefault = "/Users/henry/Downloads/TFT Screenshots/Screenshot_10.png"
Test1440PDefault = "/Users/henry/Downloads/TFT Screenshots/Screenshot_15.png"


def generate_player_list():
    return "player1", "player2", "player3", "player4", "player5", "player6", "player7", "player8"


class MyTestCase(unittest.TestCase):
    def test_parse_state_1080p(self):
        gameDebugger = debugger.Debugger()
        gameDebugger.enable_window_overlay()
        gameDebugger.enable_parse_shop()
        gameParser = parser.Parser(gameDebugger)
        gameWindow, gameBoard = initialize_screenshot(TestWindowName, Test1080PDefault)
        gameTracker = tracker.Tracker([], file_name=None)

        img = gameWindow.captureWindow()

        game.parse_state(img, gameBoard, gameTracker, gameParser, gameDebugger)
        time.sleep(10)

    def test_parse_state_1440p(self):
        gameDebugger = debugger.Debugger()
        gameDebugger.enable_window_overlay()
        gameDebugger.enable_parse_shop()
        gameParser = parser.Parser(gameDebugger)
        gameWindow, gameBoard = initialize_screenshot(TestWindowName, Test1440PDefault)
        gameTracker = tracker.Tracker([], file_name=None)

        img = gameWindow.captureWindow()

        game.parse_state(img, gameBoard, gameTracker, gameParser, gameDebugger)
        time.sleep(10)

if __name__ == '__main__':
    unittest.main()
