from tft import board, utils, window, image_utils, parser

DebugWindowName = "TFTAnalyzer Debug"
WindowName = "League of Legends (TM) Client"


def draw_debug_shapes(img, gameBoard):
    image_utils.draw_shape(img, gameBoard.getGold())
    image_utils.draw_shapes(img, gameBoard.getShop())
    image_utils.draw_shape(img, gameBoard.getLevel())
    image_utils.draw_shape(img, gameBoard.getStage())
    image_utils.draw_shapes(img, gameBoard.getHealthBars1()[0])
    image_utils.draw_shapes(img, gameBoard.getHealthBars1()[1])
    image_utils.draw_shapes(img, gameBoard.getHealthBars2()[0])
    image_utils.draw_shapes(img, gameBoard.getHealthBars2()[1])


def wait_for_window_to_appear():
    """
    Waits for the game window to begin and returns the window object

    If screenshot mode is used, the screenshot image window is created here.

    :return:
    """
    gameWindow = window.GameWindow(WindowName)
    gameWindow.waitForWindowToExist()
    return gameWindow


def initialize_game_board(gameWindow):
    """
    Initializes the various bounding boxes used to graphically parse the game and returns the board object

    The location of the bounding boxes change depending on the window size.

    :param gameWindow:
    :return:
    """
    size = gameWindow.getWindowSize()
    print("Window size: {}".format(size))
    return board.Board(size)


def retrieve_player_list(gameWindow, gameBoard):
    """

    :param gameWindow:
    :param gameBoard:
    :return:
    """
    players = []
    while not players or len(players) != 8:
        img = gameWindow.captureWindow()
        players = parser.parse_players(board.crop_players(img, gameBoard))
    print("players: {}".format(players))
    return players


def wait_for_loading_screen_to_complete(gameWindow, gameBoard):
    count = 8
    while count == 8:
        img = gameWindow.captureWindow()
        count = len(parser.parse_players(board.crop_players(img, gameBoard)))
        print("Waiting for Game to Begin (Still on Players Loading Screen)")


def parse_state(img, gameBoard, gameTracker, gameHandler):
    """
    The function will parse various information from the screenshot provided and register the data to the Tracker.

    The stage will always be parsed synchronously, as it will determine whether or not the parsing of player health
    is required.  TODO: parse other information in the background.

    :param img:
    :param gameBoard:
    :param gameTracker:
    :param gameHandler:
    :return:
    """
    stage = parser.parse_stage(board.crop_stage(img, gameBoard))
    if not utils.assert_stage_string_format(stage):
        stage = parser.parse_stage(board.crop_stage_early(img, gameBoard))

    if not utils.is_carousal_round(stage):
        level = parser.parse_level(board.crop_level(img, gameBoard))
        gold = parser.parse_gold(board.crop_gold(img, gameBoard))
        if level == -1 and gold == -1:
            return
        gameHandler.queue_shop_task(img, gameBoard, stage)

    if gameTracker.hasStageChanged(stage):
        gameHandler.queue_healthbars_task(img, gameBoard, stage)

