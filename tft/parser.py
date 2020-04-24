import cv2
import numpy as np
import pytesseract

from tft import utils, debugger


def parse_gold(img, debug=None):
    config = '--psm 8 --oem 3 -c tessedit_char_whitelist=1234567890'
    return utils.convert_string_to_integer(_parse_image_for_text(img, config, 1, debug, debugger.ParseGold))


def parse_stage(img, debug=None):
    config = '--psm 8 -c tessedit_char_whitelist=123456789-'
    return _parse_image_for_text(img, config, 1, debug, debugger.ParseStage)


def parse_level(img, debug=None):
    config = '--psm 10 --oem 3 -c tessedit_char_whitelist=123456789'
    return utils.convert_string_to_integer(_parse_image_for_text(img, config, 1, debug, debugger.ParseLevel))


def parse_shop(imgs, debug=None):
    shop = []
    for img in imgs:
        shop.append(_parse_image_for_text(img, '--psm 7', 1, debug, debugger.ParseShop))
    return shop


def parse_healthbars_legacy(top_to_bottom, bottom_to_top, debug=None):
    """
    Determines the health of each player.

    Requires two passes (from top to bottom, bottom to top) to determine all the player healths.

    :param top_to_bottom:
    :param bottom_to_top:
    :param debug:
    :return: list of tuples containing (name, health)
    """
    healthbars = []
    for img in [top_to_bottom, bottom_to_top]:
        for player in range(0, 8):
            name_config = '--psm 7 --oem 3'
            health_config = '--psm 7 -c tessedit_char_whitelist=1234567890'
            name = _parse_image_for_text(img[0][player], name_config, 1, debug, debugger.ParseHealthbars)
            health = utils.convert_string_to_integer(
                _parse_image_for_text(img[1][player], health_config, 1, debug, debugger.ParseHealthbars))
            if health != -1:
                healthbars.append((name, int(health)))
    return healthbars


def parse_players(imgs, debug=None):
    """
    Determines the players in the game from the loading screen.

    If more than 1 player is unreadable (i.e OCR returns blank), then the entire list is cleared as it is
    assumed to be not the player loading screen (black screen or past the player loading screen).

    TODO: Change return value to set

    :param imgs: cropped images of the loading screen
    :param debug:
    :return: list of players
    """
    players = []
    blank_count = 0  # TODO: Improve this logic, kinda unclear
    for img in imgs:
        possible_player = _parse_image_for_text(img, '--psm 7', 3, debug, debugger.ParsePlayers)
        if possible_player:
            player = possible_player
        else:
            blank_count += 1
            player = ""
        players.append(player)
    if blank_count > 1:
        print("Invalid Players Screen")
        players.clear()
    return players


def parse_healthbar_circles(imgs, debug=None):
    circle_points = []
    for img in imgs:
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        ret, thresh1 = cv2.threshold(blur, 65, 255, cv2.THRESH_BINARY)
        circles = cv2.HoughCircles(thresh1, cv2.HOUGH_GRADIENT, 2.0, 400)

        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                circle_points.append((x, y, r))
                if debug is not None:
                    cv2.circle(img, (x, y), r, (127, 255, 127), 4)
                    cv2.rectangle(img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        if debug is not None:
            debug.add_window(img, f"circles-{utils.generate_random_window_title()}", debugger.ParseCircles)
    return circle_points


def parse_healthbars(imgs, debug=None):
    """
    Determines the health of each player.

    :param imgs:
    :param debug:
    :return: list of tuples containing (name, health)
    """
    healthbars = []
    for player in range(0, 8):
        name_config = '--psm 7 --oem 3'
        health_config = '--psm 7 -c tessedit_char_whitelist=1234567890'
        name = ""
        if imgs[0][player] is not None:
            name = _parse_image_for_text(imgs[0][player], name_config, 1, debug, debugger.ParseHealthbars)
        health = utils.convert_string_to_integer(
            _parse_image_for_text(imgs[1][player], health_config, 4, debug, debugger.ParseHealthbars))
        if health != -1:
            healthbars.append((name, int(health)))
        else:
            cleaned_name = utils.clean_string(name)
            if cleaned_name.isdigit():
                healthbars.append(("", int(cleaned_name)))
    return healthbars


def _parse_image_for_text(img, config, pre_process, debug=None, caller=""):
    """

    TODO: cleanup pre_process values (I don't believe 2 is being used).
    pre_process values: 1 for white text, 2 for yellow text, 3 for lowered threshold (players menu),
                        4 for health values, 0 for none

    :param img:
    :param config:
    :param pre_process:
    :return:
    """
    img_processed = _pre_process_image(img, pre_process)
    text = pytesseract.image_to_string(img_processed, lang='eng', config=config)
    if debug:
        debug.add_window(img_processed, f"{text}-{utils.generate_random_window_title()}", caller)
    return text


def _pre_process_image(img, mode):
    if mode == 0:
        return img
    if mode == 4:
        frame_HSV = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        img_processed = cv2.inRange(frame_HSV, (0, 0, 127), (180, 100, 255))
        kernel = np.ones((1, 1), np.uint8)
        img_processed = cv2.morphologyEx(img_processed, cv2.MORPH_CLOSE, kernel)
        return cv2.bitwise_not(img_processed)
    img_masked = img
    if mode == 2:
        lower_red = np.array([62, 117, 60])
        upper_red = np.array([218, 228, 213])
        mask = cv2.inRange(img, lower_red, upper_red)
        img_masked = cv2.bitwise_and(img, img, mask=mask)
    gray = cv2.cvtColor(img_masked, cv2.COLOR_RGB2GRAY)
    thresh_target = 127 if mode != 3 else 80
    ret, thresh1 = cv2.threshold(gray, thresh_target, 255, cv2.THRESH_BINARY)
    return cv2.inRange(thresh1, 0, 0)
