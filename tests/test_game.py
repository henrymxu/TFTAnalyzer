import time
import unittest

from tests import initialize_screenshot
from tft import game, debugger, parser, tracker, window

Test1080PDefaultScreenshot = "/Users/henry/Downloads/TFT Screenshots/Screenshot_10.png"
Test1440PDefaultScreenshot = "/Users/henry/Downloads/TFT Screenshots/Screenshot_15.png"

Test1080PDefaultRecording = "/Users/henry/Videos/2020-04-16 17-28-07.mkv"
Test1440PDefaultRecording = "/Users/henry/Videos/2020-04-16 13-37-15.mkv"


def generate_player_list():
    return "player1", "player2", "player3", "player4", "player5", "player6", "player7", "player8"


class MyTestCase(unittest.TestCase):
    def test_parse_state_1080p_screenshot(self):
        gameDebugger = debugger.Debugger()
        gameDebugger.enable_window_overlay()
        gameDebugger.enable_parse_shop()
        gameParser = parser.Parser(gameDebugger)
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefaultScreenshot)
        gameTracker = tracker.Tracker([], file_name=None)

        img = gameWindow.captureWindow()

        game.parse_state(img, gameBoard, gameTracker, gameParser, gameDebugger)
        time.sleep(10)

    def test_parse_state_1440p_screenshot(self):
        gameDebugger = debugger.Debugger()
        gameDebugger.enable_window_overlay()
        gameDebugger.enable_parse_shop()
        gameParser = parser.Parser(gameDebugger)
        gameWindow, gameBoard = initialize_screenshot(Test1440PDefaultScreenshot)
        gameTracker = tracker.Tracker([], file_name=None)

        img = gameWindow.captureWindow()

        game.parse_state(img, gameBoard, gameTracker, gameParser, gameDebugger)
        time.sleep(10)

    def test_parse_state_1440p_video(self):
        gameDebugger = debugger.Debugger()
        gameDebugger.enable_window_overlay()
        gameDebugger.enable_parse_shop()
        gameDebugger.enable_parse_gold()

        gameParser = parser.Parser(gameDebugger)
        gameWindow = window.PreRecordedGameplayWindow(Test1440PDefaultRecording)
        gameWindow.showWindow()
        gameBoard = game.initialize_game_board(gameWindow)
        players = game.retrieve_player_list(gameWindow, gameBoard, gameParser, gameDebugger)

        file_name = None
        gameTracker = tracker.Tracker(players, file_name=file_name)

        while True:
            if not gameWindow.doesWindowExist():
                print("Game has completed or crashed, assume completed")
                break
            img = gameWindow.captureWindow()
            game.parse_state(img, gameBoard, gameTracker, gameParser, gameDebugger)


if __name__ == '__main__':
    unittest.main()
