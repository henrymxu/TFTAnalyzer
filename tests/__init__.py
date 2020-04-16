from tft import window, image_utils, game


def initialize_screenshot(window_name, file_name):
    gameWindow = window.StaticImageWindow(window_name, file_name)
    gameWindow.showWindow()
    gameBoard = game.initialize_game_board(gameWindow)
    return gameWindow, gameBoard
