from tft import board, utils, tracker, window, image_utils

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


def wait_for_game_to_begin(screenshot=False):
    """
    Waits for the game window to begin and returns the window object

    If screenshot mode is used, the screenshot image window is created here.

    :param screenshot:
    :return:
    """
    gameWindow = window.GameWindow(WindowName)
    if screenshot:
        gameWindow = window.StaticImageWindow(DebugWindowName)
        image = gameWindow.captureWindow()
        image_utils.show_image(image, DebugWindowName)
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
    return board.GameBoard(size)


def retrieve_player_list(gameWindow, gameBoard):
    """

    :param gameWindow:
    :param gameBoard:
    :return:
    """
    players = []
    while len(players) != 8:
        image = gameWindow.captureWindow()
        players = tracker.determine_players(image_utils.crop_shapes(image, gameBoard.getPlayers()))
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
        stage = tracker.determine_stage(image_utils.crop_shape(img, gameBoard.getStage()[0], 200))
        level = tracker.determine_level(image_utils.crop_shape(img, gameBoard.getLevel()[0], 150))
        gold = tracker.determine_gold(image_utils.crop_shape(img, gameBoard.getGold()[0], 150))
        shop = tracker.determine_shop(image_utils.crop_shapes(img, gameBoard.getShop(), 200))
        print("default info gathering exec time: {} seconds".format(utils.end_timer(timer)))

        print("stage {}, level {}, gold {}".format(stage, level, gold))
        print("shop {}".format(shop))

        if gameTracker.hasShopChanged(shop):
            gameTracker.addShop(shop, stage, level, gold)

        if gameTracker.hasStageChanged(stage):
            top_to_bottom = (image_utils.crop_shapes(img, gameBoard.getHealthBars1()[0], 150),
                             image_utils.crop_shapes(img, gameBoard.getHealthBars1()[1], 200))
            bottom_to_top = (image_utils.crop_shapes(img, gameBoard.getHealthBars2()[0], 150),
                             image_utils.crop_shapes(img, gameBoard.getHealthBars2()[1], 200))
            timer = utils.start_timer()
            healthbars = tracker.determine_healthbars((top_to_bottom, bottom_to_top))
            print("healthbars gathering exec time: {} seconds".format(utils.end_timer(timer)))
            print("healthbars {}".format(healthbars))
            gameTracker.addStage(stage)

        if debug:
            debug_screen(img, gameBoard)
