import time
import unittest

from tests import initialize_screenshot, initialize_video
from tft import game, debugger, tracker, main

Test1080PDefaultScreenshot = "/Users/henry/Downloads/TFT Screenshots/Screenshot_10.png"
Test1440PDefaultScreenshot = "/Users/henry/Downloads/TFT Screenshots/Screenshot_15.png"

Test1080PDefaultRecording = "/Users/henry/Downloads/TFT Screenshots/video_1080_4.mkv"
Test1440PDefaultRecording = "/Users/henry/Downloads/TFT Screenshots/video_1440_1.mkv"


def generate_player_list():
    return "player1", "player2", "player3", "player4", "player5", "player6", "player7", "player8"


class TestGame(unittest.TestCase):
    def test_parse_state_1080p_screenshot(self):
        gameWindow, gameBoard = initialize_screenshot(Test1080PDefaultScreenshot)
        gameTracker = tracker.Tracker([], file_name=None)

        img = gameWindow.captureWindow()

        game.parse_state(img, gameBoard, gameTracker)
        time.sleep(10)

    def test_parse_state_1440p_screenshot(self):
        gameWindow, gameBoard = initialize_screenshot(Test1440PDefaultScreenshot)
        gameTracker = tracker.Tracker([], file_name=None)

        img = gameWindow.captureWindow()

        game.parse_state(img, gameBoard, gameTracker)
        time.sleep(10)

    def test_parse_state_1440p_video(self):
        gameWindow = initialize_video(Test1440PDefaultRecording)
        main.main(gameWindow)

    def test_parse_state_1080p_video(self):
        gameWindow = initialize_video(Test1080PDefaultRecording)
        main.main(gameWindow)


if __name__ == '__main__':
    unittest.main()
