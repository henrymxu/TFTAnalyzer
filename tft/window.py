import time

import cv2
import numpy as np
import win32gui
from PIL import ImageGrab


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



class StaticImageWindow(GameWindow):
    def __init__(self, name, file_name):
        super().__init__(name)
        self._file_name = file_name

    def captureWindow(self):
        image = cv2.imread(self._file_name)
        return image

    def waitForWindowToExist(self):
        return


def get_foreground_window():
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())
