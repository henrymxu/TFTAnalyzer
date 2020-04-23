import time
import unittest

from tests import initialize_screenshot, initialize_video
from tft import game, tracker, main, handler

Test1080PDefaultScreenshot = "/Users/henry/Downloads/TFT Screenshots/Screenshot_10.png"
Test1440PDefaultScreenshot = "/Users/henry/Downloads/TFT Screenshots/Screenshot_15.png"

Test1080PDefaultRecording = "/Users/henry/Downloads/TFT Screenshots/video_1080_4.mkv"
Test1440PDefaultRecording = "/Users/henry/Downloads/TFT Screenshots/video_1440_2.mkv"


def generate_player_list():
    return "player1", "player2", "player3", "player4", "player5", "player6", "player7", "player8"


class TestGame(unittest.TestCase):
    def test_parse_state_1080p_screenshot(self):
        test_screenshot(self, Test1080PDefaultScreenshot)

    def test_parse_state_1440p_screenshot(self):
        test_screenshot(self, Test1440PDefaultScreenshot)

    def test_parse_state_1440p_video(self):
        gameWindow = initialize_video(Test1440PDefaultRecording)
        main.main(gameWindow)

    def test_parse_state_1080p_video(self):
        gameWindow = initialize_video(Test1080PDefaultRecording)
        main.main(gameWindow, "test/testing_2.json")

def test_screenshot(testcase, file_name):
    gameWindow, gameBoard = initialize_screenshot(file_name)
    gameTracker = tracker.Tracker([], file_name=None)
    gameHandler = handler.Handler(gameTracker.getEntryQueue())

    img = gameWindow.captureWindow()

    game.parse_state(img, gameBoard, gameTracker, gameHandler)
    time.sleep(10)

if __name__ == '__main__':
    unittest.main()
