from tft import tracker, game, handler


def generate_file_name():
    import time
    ts = time.time()
    return "test/{}.json".format(str(int(ts)))


def main(gameWindow, file_name=None):
    gameBoard = game.initialize_game_board(gameWindow)

    players = game.retrieve_player_list(gameWindow, gameBoard)
    game.wait_for_loading_screen_to_complete(gameWindow, gameBoard)

    gameTracker = tracker.Tracker(players, file_name=file_name)
    gameTracker.track()
    gameHandler = handler.Handler(gameTracker.getEntryQueue())
    gameHandler.start()

    while True:
        if not gameWindow.doesWindowExist():
            print("Game has completed or crashed, assume completed")
            break
        img = gameWindow.captureWindow()
        if img is None:
            break
        game.parse_state(img, gameBoard, gameTracker, gameHandler)

    gameWindow.closeWindowIfNeeded()
    gameHandler.finish()
    gameTracker.writeToFile()

    # TODO: Implement cleaner and analyzer for file


if __name__ == "__main__":
    gameWindow = game.wait_for_window_to_appear()
    file_name = generate_file_name()
    main(gameWindow, file_name)
