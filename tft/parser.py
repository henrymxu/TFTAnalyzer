import cv2
import numpy as np
import pytesseract


def parse_gold(img):
    return _parse_image_for_text(img, '--psm 8 --oem 3 -c tessedit_char_whitelist=1234567890', pre_process=False)


def parse_stage(img):
    return _parse_image_for_text(img, '--psm 8 -c tessedit_char_whitelist=123456789-')


def parse_level(img):
    return _parse_image_for_text(img, '--psm 10 --oem 3 -c tessedit_char_whitelist=123456789', pre_process=False)


def parse_shop(imgs):
    shop = []
    for img in imgs:
        shop.append(_parse_unit(img))
    return shop


def _parse_unit(image):
    return _parse_image_for_text(image, '--psm 7')


def parse_healthbars(img_directions):
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


def parse_players(images):
    """
    Determines the players in the game from the loading screen
    :param images: image of the loading screen
    :return: list of players
    """
    players = []
    for image in images:
        players.append(_parse_image_for_text(image, '--psm 7'))


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
