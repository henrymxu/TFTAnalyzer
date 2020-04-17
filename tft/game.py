from tft import board, utils, window, image_utils, parser, debugger

DebugWindowName = "TFTAnalyzer Debug"
WindowName = "League of Legends (TM) Client"


def draw_debug_shapes(img, game):
    image_utils.draw_shape(img, game.getGold())
    image_utils.draw_shapes(img, game.getShop())
    image_utils.draw_shape(img, game.getLevel())
    image_utils.draw_shape(img, game.getStage())
    image_utils.draw_shapes(img, game.getHealthBars1()[0])
    image_utils.draw_shapes(img, game.getHealthBars1()[1])
    image_utils.draw_shapes(img, game.getHealthBars2()[0])
    image_utils.draw_shapes(img, game.getHealthBars2()[1])


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


def retrieve_player_list(gameWindow, gameBoard, gameParser, gameDebugger=None):
    """

    :param gameWindow:
    :param gameBoard:
    :param gameParser:
    :param gameDebugger:
    :return:
    """
    players = []
    while not players or len(players) != 8:
        img = gameWindow.captureWindow()
        players = gameParser.parse_players(board.crop_players(img, gameBoard))
        if gameDebugger:
            image_utils.draw_shapes(img, gameBoard.getPlayers())
            gameDebugger.add_window(img, DebugWindowName, debugger.PlayerWindowOverlay)
            gameDebugger.show()
    print("players: {}".format(players))
    return players


def wait_for_loading_screen_to_complete(gameWindow, gameBoard, gameParser):
    count = 8
    while count == 8:
        img = gameWindow.captureWindow()
        count = len(gameParser.parse_players(board.crop_players(img, gameBoard)))
        print("Waiting for Game to Begin (Still on Players Loading Screen)")


def parse_state(img, gameBoard, gameTracker, gameParser, gameDebugger=None):
    """
    Polls the game state and retrieves various information

    The function will capture a screenshot of the game and attempt to determine various sets of information.

    :param img:
    :param gameBoard:
    :param gameTracker:
    :param gameDebugger:
    :return:
    """
    timer = utils.start_timer()
    stage = gameParser.parse_stage(board.crop_stage(img, gameBoard))
    level = gameParser.parse_level(board.crop_level(img, gameBoard))
    gold = gameParser.parse_gold(board.crop_gold(img, gameBoard))
    shop = gameParser.parse_shop(board.crop_shop(img, gameBoard))
    print("default info gathering exec time: {} seconds".format(utils.end_timer(timer)))
    print("stage {}, level {}, gold {}, shop {}".format(stage, level, gold, shop))

    if gameTracker.hasStageChanged(stage):
        top_to_bottom = board.crop_healthbar(img, gameBoard, 0)
        bottom_to_top = board.crop_healthbar(img, gameBoard, 1)
        timer = utils.start_timer()
        healthbars = gameParser.parse_healthbars(top_to_bottom, bottom_to_top)
        print("healthbars gathering exec time: {} seconds".format(utils.end_timer(timer)))
        print("healthbars {}".format(healthbars))
        gameTracker.addStage(stage, healthbars, level, gold)

    gameTracker.addShopIfChanged(shop, stage, level, gold)

    if gameDebugger:
        draw_debug_shapes(img, gameBoard)
        gameDebugger.add_window(img, DebugWindowName, debugger.WindowOverly)
        gameDebugger.show()
