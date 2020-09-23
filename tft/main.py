from tft import tracker, game, handler


def main(gameWindow, gameDebugger=None, file_name=None):
    gameBoard = game.initialize_game_board(gameWindow)

    players = game.retrieve_player_list(gameWindow, gameBoard, gameDebugger)
    game.wait_for_loading_screen_to_complete(gameWindow, gameBoard)

    gameTracker = tracker.Tracker(players, file_name=file_name)
    gameTracker.track()
    gameHandler = handler.Handler(gameTracker.getEntryQueue(), gameDebugger)
    gameHandler.start()

    while True:
        if not gameWindow.doesWindowExist():
            print("Game has completed or crashed, assume completed")
            break
        img = gameWindow.captureWindow()
        if img is None:
            break
        game.parse_state(img, gameBoard, gameTracker, gameHandler)

        if gameDebugger:
            gameDebugger.show()

    gameWindow.closeWindowIfNeeded()
    gameHandler.finish()
    gameTracker.writeToFile()

    # TODO: Implement cleaner and analyzer for file
