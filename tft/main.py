from tft import tracker, game, parser


def generate_file_name():
    import time
    ts = time.time()
    return "test/{}.json".format(str(int(ts)))


def main():
    gameParser = parser.Parser()
    gameWindow = game.wait_for_window_to_appear()
    gameBoard = game.initialize_game_board(gameWindow)

    players = game.retrieve_player_list(gameWindow, gameBoard, gameParser)
    game.wait_for_loading_screen_to_complete(gameWindow, gameBoard, gameParser)

    file_name = generate_file_name()
    gameTracker = tracker.Tracker(players, file_name=file_name)

    while True:
        if not gameWindow.doesWindowExist():
            print("Game has completed or crashed, assume completed")
            break
        img = gameWindow.captureWindow()

        game.parse_state(img, gameBoard, gameTracker, gameParser)

    gameTracker.writeToFile()
    # TODO: Implement cleaner and analyzer for file


if __name__ == "__main__":
    main()
