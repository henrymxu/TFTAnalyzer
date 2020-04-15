import cv2
import numpy as np
import pytesseract

from tft import debugger


class Parser:
    def __init__(self, debugger=None):
        self.__debugger = debugger

    def parse_gold(self, img):
        config = '--psm 8 --oem 3 -c tessedit_char_whitelist=1234567890'
        return self._parse_image_for_text(img, config, False, debugger.ParseGold)

    def parse_stage(self, img):
        config = '--psm 8 -c tessedit_char_whitelist=123456789-'
        return self._parse_image_for_text(img, config, True, debugger.ParseStage)

    def parse_level(self, img):
        config = '--psm 10 --oem 3 -c tessedit_char_whitelist=123456789'
        return self._parse_image_for_text(img, config, False, debugger.ParseLevel)

    def parse_shop(self, imgs):
        shop = []
        for img in imgs:
            shop.append(self._parse_image_for_text(img, '--psm 7', True, debugger.ParseShop))
        return shop

    def parse_healthbars(self, top_to_bottom, bottom_to_top):
        """
        Determines the health of each player.

        Requires two passes (from top to bottom, bottom to top) to determine all the player healths.

        :param top_to_bottom:
        :param bottom_to_top:
        :return:
        """
        healthbars = []
        for img in [top_to_bottom, bottom_to_top]:
            for player in range(0, 8):
                name_config = '--psm 7 --oem 3'
                health_config = '--psm 7 -c tessedit_char_whitelist=1234567890'
                name = self._parse_image_for_text(img[0][player], name_config, True, debugger.ParseHealthbars)
                health = self._parse_image_for_text(img[1][player], health_config, True, debugger.ParseHealthbars)
                if health.isnumeric():
                    healthbars.append((name, health))
        return healthbars

    def parse_players(self, imgs):
        """
        Determines the players in the game from the loading screen
        :param imgs: cropped images of the loading screen
        :return: list of players
        """
        players = []
        for img in imgs:
            possible_player = self._parse_image_for_text(img, '--psm 7', True, debugger.ParsePlayers)
            player = possible_player if possible_player else "You"
            players.append(player)
        return players

    def _parse_image_for_text(self, img, config, pre_process, caller=""):
        img_processed = img
        if pre_process:
            lower_red = np.array([60, 117, 62])
            upper_red = np.array([213, 228, 218])

            mask = cv2.inRange(img, lower_red, upper_red)
            res = cv2.bitwise_and(img, img, mask=mask)

            gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
            ret, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            img_processed = cv2.inRange(thresh1, 0, 0)
        text = pytesseract.image_to_string(img_processed, lang='eng', config=config)
        if self.__debugger:
            from tft import utils
            self.__debugger.add_window(img_processed, "{} - {}".format(text, utils.generate_random_window_title()),
                                       caller)
        return text
