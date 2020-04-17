from tft import tracker, game, debugger, parser


def generate_file_name():
    import time
    ts = time.time()
    return "test/{}.json".format(str(int(ts)))


def main():
    gameDebugger = debugger.Debugger()
    gameParser = parser.Parser(gameDebugger)

    gameWindow = game.wait_for_window_to_appear()
    gameBoard = game.initialize_game_board(gameWindow)

    players = game.retrieve_player_list(gameWindow, gameBoard, gameParser, gameDebugger)
    game.wait_for_loading_screen_to_complete(gameWindow, gameBoard, gameParser)

    file_name = generate_file_name() if not gameDebugger else None
    gameTracker = tracker.Tracker(players, file_name=file_name)

    while True:
        if not gameWindow.doesWindowExist():
            print("Game has completed or crashed, assume completed")
            break
        img = gameWindow.captureWindow()

        game.parse_state(img, gameBoard, gameTracker, gameParser, gameDebugger)

    gameTracker.writeToFile()


main()
