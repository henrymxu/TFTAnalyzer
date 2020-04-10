import time

import cv2
import numpy as np
import pytesseract
from fuzzywuzzy import process, fuzz

from tft import utils


class Tracker:
    def __init__(self, players, write=True):
        self.__unitLookupTable = self._initializeUnitLookupTable()
        self.__shops = []
        self.__state = {}
        self.__players = players
        self.__write = write
        if write:
            ts = time.time()
            self.__fileName = "test/{}.json".format(str(int(ts)))
            utils.create_json_file(self.__fileName)

    def _initializeUnitLookupTable(self):
        """
        Initialize the unit lookup table using json file provided from Riot (supports Set2 and Set3)

        :return:
        """
        unit_lookup_table = []
        json = utils.open_json_file("data/champions_set3.json")
        for unit in json:
            key = "name"  # Set 3 key
            if key not in unit:
                key = "champion"  # Set 2 key
            unit_lookup_table.append(unit[key])
        return unit_lookup_table

    def _findUnitInLookupTable(self, unit):
        """
        Attempts to find unit in lookup table

        Uses Fuzzy string matching in order to find the correct unit.  If the best match has a score lower than
        75, a blank string will be returned instead.

        :param unit: post processed string representing a unit
        :return: string
        """
        if unit == "" or unit == "Be":  # Weird case where empty shop tile appears as "Be"
            return ""
        choice = process.extract(unit, self.__unitLookupTable, limit=1, scorer=fuzz.QRatio)
        if choice[0][1] <= 75:
            # print("Not a Match: {} != {}, score = {}".format(unit, choice[0][0], choice[0][1]))
            return ""
        # print("Found Match: {} == {}, score = {}".format(unit, choice[0][0], choice[0][1]))
        return choice[0][0]

    def hasShopChanged(self, units):
        """
        Determines whether or not the shop has changed.

        New shop items are compared to the previous shop items.  If 2 or more slots have different units,
        then the shop is considered changed.

        TODO: check gold/stage?

        :param units: list of post-processed units (validated and corrected with UnitLookupTable)
        :return: boolean
        """
        units_changed = 0
        for i in range(0, 5):
            if units[i] == "":
                continue
            if not self.__shops:
                return True
            if not self.__shops[-1]["units"][i] == units[i]:
                units_changed += 1
        return units_changed > 1

    def hasStageChanged(self, stage):
        """
        Determines whether or not the stage has changed.

        :param stage: string with format (x-y)
        :return: boolean
        """
        if self.__state and self.__state["stage"] and self.__state["stage"] == stage:
            return False
        return True

    def addStage(self, stage, healthbars, level, gold):
        if self.__state and self.__write:
            utils.append_to_json_file(self.__fileName, self.__state)
        self.__shops.clear()
        self.__state = _create_state(stage, healthbars, level, gold, self.__shops)

    def addShopIfChanged(self, units, level, gold):
        """
        Add a shop to the tracker if has yet to be added, along with the current level and gold amount.

        :param units: list of pre-processed units
        :param level:
        :param gold:
        :return: boolean
        """
        units = [self._findUnitInLookupTable(i) for i in units]
        if not self.hasShopChanged(units):
            return False
        shop = _create_shop(units, level, gold)
        self.__shops.append(shop)
        return True


def _create_shop(units, level, gold):
    return {"units": units, "level": level, "gold": gold}


def _create_state(stage, healthbars, level, gold, shops):
    return {"stage": stage, "healthbars": healthbars, "level": level, "gold": gold, "shops": shops}


def determine_gold(img):
    return _parse_image_for_text(img, '--psm 8 --oem 3 -c tessedit_char_whitelist=1234567890', pre_process=False)


def determine_stage(img):
    return _parse_image_for_text(img, '--psm 8 -c tessedit_char_whitelist=123456789-')


def determine_level(img):
    return _parse_image_for_text(img, '--psm 10 --oem 3 -c tessedit_char_whitelist=123456789', pre_process=False)


def determine_shop(imgs):
    shop = []
    for img in imgs:
        shop.append(determine_unit(img))
    return shop


def determine_unit(image):
    return _parse_image_for_text(image, '--psm 7')


def determine_healthbars(img_directions):
    """
    Determines the health of each player.

    Requires two passes (from top to bottom, bottom to top) to determine all the player healths.

    :param img_directions: list in which each element contains 2 images (one for the player names, one for the healths)
    :return:
    """
    healthbars = []
    for img in img_directions:
        for player in range(0, 8):
            name = _parse_image_for_text(img[0][player], '--psm 7 --oem 3')
            health = _parse_image_for_text(img[1][player], '--psm 7 -c tessedit_char_whitelist=1234567890')

            if health.isnumeric():
                healthbars.append((name, health))
    return healthbars


def determine_players(images):
    players = []
    for image in images:
        players.append(determine_unit(image))


def _parse_image_for_text(image, config, pre_process=True):
    img_processed = image
    if pre_process:
        lower_red = np.array([60, 117, 62])
        upper_red = np.array([213, 228, 218])

        mask = cv2.inRange(image, lower_red, upper_red)
        res = cv2.bitwise_and(image, image, mask=mask)

        gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
        ret, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        img_processed = cv2.inRange(thresh1, 0, 0)
    text = pytesseract.image_to_string(img_processed, lang='eng', config=config)
    # title = text
    # if text == "":
    #     title = utils.generate_random_window_title()
    # cv2.imshow(title, img_processed)
    return text
