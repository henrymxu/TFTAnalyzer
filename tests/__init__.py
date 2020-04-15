from tft import window, image_utils, game


def initialize_screenshot(window_name, file_name):
    gameWindow = window.StaticImageWindow(window_name, file_name)
    image = gameWindow.captureWindow()
    image_utils.show_image(image, window_name)
    gameBoard = game.initialize_game_board(gameWindow)
    return gameWindow, gameBoard
