from tft import board, utils, window, image_utils, parser

DebugWindowName = "TFTAnalyzer Debug"
WindowName = "League of Legends (TM) Client"


def debug_screen(img, game):
    image_utils.draw_shape(img, game.getGold())
    image_utils.draw_shapes(img, game.getShop())
    image_utils.draw_shape(img, game.getLevel())
    image_utils.draw_shape(img, game.getStage())
    image_utils.draw_shapes(img, game.getHealthBars1()[0])
    image_utils.draw_shapes(img, game.getHealthBars1()[1])
    image_utils.draw_shapes(img, game.getHealthBars2()[0])
    image_utils.draw_shapes(img, game.getHealthBars2()[1])
    image_utils.show_image(img, DebugWindowName)


def wait_for_game_to_begin():
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
    return board.gameBoard(size)


def retrieve_player_list(gameWindow, gameBoard, debug=False):
    """

    :param gameWindow:
    :param gameBoard:
    :param debug:
    :return:
    """
    players = []
    while not players or len(players) != 8:
        img = gameWindow.captureWindow()
        players = parser.parse_players(board.crop_players(img, gameBoard))
        if debug:
            image_utils.draw_shapes(img, gameBoard.getPlayers())
            image_utils.show_image(img, DebugWindowName)
            import cv2
            cv2.waitKey(250)
    print("players: {}".format(players))
    return players


def track_game(gameWindow, gameBoard, gameTracker, debug=False):
    """
    Polls the game state and retrieves various information

    The function will capture a screenshot of the game and attempt to determine various sets of information.

    :param gameWindow:
    :param gameBoard:
    :param gameTracker:
    :param debug:
    :return:
    """
    while True:
        if not gameWindow.doesWindowExist():
            print("Game has completed or crashed, assume completed")
            break
        img = gameWindow.captureWindow()

        timer = utils.start_timer()
        stage = parser.parse_stage(board.crop_stage(img, gameBoard))
        level = parser.parse_level(board.crop_level(img, gameBoard))
        gold = parser.parse_gold(board.crop_gold(img, gameBoard))
        shop = parser.parse_shop(board.crop_shop(img, gameBoard))
        print("default info gathering exec time: {} seconds".format(utils.end_timer(timer)))
        print("stage {}, level {}, gold {}, shop {}".format(stage, level, gold, shop))

        if gameTracker.hasStageChanged(stage):
            top_to_bottom = board.crop_healthbar(img, gameBoard, 0)
            bottom_to_top = board.crop_healthbar(img, gameBoard, 1)
            timer = utils.start_timer()
            healthbars = parser.parse_healthbars(top_to_bottom, bottom_to_top)
            print("healthbars gathering exec time: {} seconds".format(utils.end_timer(timer)))
            print("healthbars {}".format(healthbars))
            gameTracker.addStage(stage, healthbars, level, gold)

        gameTracker.addShopIfChanged(shop, stage, level, gold)

        if debug:
            debug_screen(img, gameBoard)
