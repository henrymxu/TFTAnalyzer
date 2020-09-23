import time
import unittest

from tests import initialize_screenshot, initialize_video
from tft import game, tracker, main, handler, debugger, utils

Test1080PDefaultScreenshot = "/Users/henry/Downloads/TFT Screenshots/board_1080_1.png"
Test1440PDefaultScreenshot = "/Users/henry/Downloads/TFT Screenshots/board_1440_5.png"

Test1080PDefaultRecording = "/Users/henry/Downloads/TFT Screenshots/video_1080_3_short_3.mp4"
Test1440PDefaultRecording = "/Users/henry/Downloads/TFT Screenshots/video_1440_3.mkv"


def generate_player_list():
    return "player1", "player2", "player3", "player4", "player5", "player6", "player7", "player8"


class TestGame(unittest.TestCase):
    def test_parse_state_1080p_screenshot(self):
        test_screenshot(self, Test1080PDefaultScreenshot)

    def test_parse_state_1440p_screenshot(self):
        test_screenshot(self, Test1440PDefaultScreenshot)

    def test_parse_state_1440p_video(self):
        gameDebugger = debugger.Debugger()
        gameWindow = initialize_video(Test1440PDefaultRecording)
        main.main(gameWindow, gameDebugger, f"test/testing_1440_{utils.generate_file_name()}")

    def test_parse_state_1080p_video(self):
        gameDebugger = debugger.Debugger()
        gameWindow = initialize_video(Test1080PDefaultRecording)
        main.main(gameWindow, gameDebugger, f"test/testing_1080_{utils.generate_file_name()}")


def test_screenshot(testcase, file_name):
    gameWindow, gameBoard = initialize_screenshot(file_name)
    gameTracker = tracker.Tracker([], file_name=None)
    gameHandler = handler.Handler(gameTracker.getEntryQueue())

    img = gameWindow.captureWindow()

    game.parse_state(img, gameBoard, gameTracker, gameHandler)
    time.sleep(10)


if __name__ == '__main__':
    unittest.main()
