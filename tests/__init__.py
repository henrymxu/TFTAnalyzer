from tft import window, game

TestWindowName = "TFTAnalyzer Test Window"


def initialize_screenshot(file_name, window_name=TestWindowName):
    gameWindow = window.StaticImageWindow(window_name, file_name)
    gameWindow.showWindow()
    gameBoard = game.initialize_game_board(gameWindow)
    return gameWindow, gameBoard

def initialize_video(file_name, window_name=TestWindowName):
    gameWindow = window.PreRecordedGameplayWindow(window_name, file_name)
    gameWindow.showWindow()
    return gameWindow