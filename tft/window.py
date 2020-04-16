import time

import cv2
import numpy as np
import win32gui
from PIL import ImageGrab

from tft import image_utils


class GameWindow:
    def __init__(self, name):
        self._title = name

    def findWindow(self):
        return win32gui.FindWindow(None, self._title)

    def getWindowCoordinates(self):
        hwnd = self.findWindow()
        left, top, right, bot = win32gui.GetClientRect(hwnd)
        left, top = win32gui.ClientToScreen(hwnd, (left, top))
        return left, top, left + right, top + bot

    def getWindowSize(self):
        left, top, right, bot = win32gui.GetClientRect(self.findWindow())
        return right - left, bot - top

    # def moveWindow(self):
    #     hwnd = self.findWindow()
    #     if hwnd == 0:
    #         return False
    #     win32gui.MoveWindow(hwnd, 0, 0, self._size[0], self._size[1], True)
    #     return True

    def captureWindow(self):
        self.waitForWindowToExist()
        self.waitForWindowToBeInForeground()
        coords = self.getWindowCoordinates()
        return np.array(ImageGrab.grab(bbox=coords))

    def waitForWindowToExist(self):
        while not self.doesWindowExist():
            print("Looking for {}".format(self._title))
            time.sleep(5)
        return

    def waitForWindowToBeInForeground(self):
        while get_foreground_window() != self._title:
            pass
        return

    def doesWindowExist(self):
        return self.findWindow() != 0

    def showWindow(self):
        # This class does not need to implement this function as the program does not need to show a window.
        return


class StaticImageWindow(GameWindow):
    def __init__(self, name, file_name):
        super().__init__(name)
        self._file_name = file_name
        self._image = None

    def captureWindow(self):
        return self._image

    def waitForWindowToExist(self):
        return

    def showWindow(self):
        image = cv2.imread(self._file_name)
        self._image = image
        image_utils.show_image(image, self._title)


class PreRecordedGameplayWindow(GameWindow):
    def __init__(self, name, file_name):
        super().__init__(name)
        self._file_name = file_name
        self._freq = 60
        self._cap = None

    def captureWindow(self):
        """
        Capture a frame from the pre-recorded gameplay.  It will also iterate the gameplay forward by a set amount
        of frames.

        :return:
        """
        cap = self._cap
        frame = None
        for _ in range(0, self._freq):
            if not cap.isOpened():
                cap.release()
                cv2.destroyAllWindows()
                return frame

            ret, frame = cap.read()
            cv2.imshow(self._title, frame)
            cv2.waitKey(1)

        return frame

    def showWindow(self):
        self._cap = cv2.VideoCapture(self._file_name)
        ret, frame = self._cap.read()
        cv2.imshow(self._title, frame)
        cv2.waitKey(1)


def get_foreground_window():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())
