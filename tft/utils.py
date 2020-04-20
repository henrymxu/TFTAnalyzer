import json
import os
import re
import sys
import time
import cv2
import pyautogui
from fuzzywuzzy import process, fuzz

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


def assert_stage_string_format(stage):
    """

    :param stage:
    :return: boolean
    """
    results = re.search("[1-9]-[1-9]", stage)
    return results is not None


def parse_stage_round(stage):
    if not assert_stage_string_format(stage):
        return 0, 0
    return convert_string_to_integer(stage[0]), convert_string_to_integer(stage[2])


def is_carousal_round(stage):
    parsed_stage = parse_stage_round(stage)
    return parsed_stage[0] != 1 and parsed_stage[1] == 4 or parsed_stage[0] == 1 and parsed_stage[1] == 1


def find_matching_string_in_list(string, lookup_list, score=70):
    """
    Attempts to match a string to an element in a list

    Uses Fuzzy string matching in order to find the correct string.  If the best match has a score lower than
    than the score provided, a blank string will be returned instead.

    :param string:
    :param lookup_list:
    :param score:
    :return:
    """
    import fuzzywuzzy.utils
    if string == "" or string == "Be":  # Weird case where empty shop tile appears as "Be"
        return ""
    string = fuzzywuzzy.utils.full_process(string)
    choice = process.extract(string, lookup_list, limit=1, scorer=fuzz.QRatio)
    if not choice or choice[0][1] < score:
        print("Not a Match: {} != {}, score = {}".format(string, choice[0][0], choice[0][1]))
        return ""
    # print("Found Match: {} == {}, score = {}".format(string, choice[0][0], choice[0][1]))
    return choice[0][0]


def convert_string_to_integer(string):
    return int(string) if string.isdigit() else -1
