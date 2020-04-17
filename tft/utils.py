import json
import os
import re
import sys
import time
import cv2
import pyautogui

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


# TODO: Remove
def onMouseClick(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print('x = %d, y = %d' % (x, y))
    # draw circle here (etc...)


# TODO: Remove
def dragMouse():
    pyautogui.moveTo(100, 150)
    pyautogui.moveRel(0, 10)  # move mouse 10 pixels down
    pyautogui.dragTo(100, 150)
    pyautogui.dragRel(0, 10)  # drag mouse 10 pixels down


# TODO: Remove
def mouseStuff():
    # cv2.setMouseCallback('window', debugger.onMouseClick)
    # if cv2.waitKey(25) & 0xFF == ord('q'):
    #     cv2.destroyAllWindows()
    #     break
    # elif cv2.waitKey(25) & 0xFF == ord('c'):
    #     continue
    pass


def start_timer():
    return time.time()


def end_timer(start):
    diff = int(time.time() - start)
    return diff


def open_json_file(file):
    with open(os.path.join(_ROOT, file)) as json_file:
        data = json.load(json_file)
    return data


def create_json_array_file(file):
    with open(os.path.join(_ROOT, file), mode='w', encoding='utf-8') as f:
        json.dump([], f)


def append_to_json_array_file(file, data):
    with open(os.path.join(_ROOT, file), mode='r', encoding='utf-8') as feed:
        feeds = json.load(feed)
    with open(os.path.join(_ROOT, file), mode='w', encoding='utf-8') as feed:
        feeds.append(data)
        json.dump(feeds, feed)


def delete_json_file(file):
    os.remove(os.path.join(_ROOT, file))


def exit_with_error(string):
    sys.exit(string)


def generate_random_window_title():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


def retain_only_digits(string):
    return re.sub("\D", "", string)


def assert_stage_regex(stage):
    """

    :param stage:
    :return:
    """
    results = re.search("[1-9]-[1-9]", stage)
    return results is not None
