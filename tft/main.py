from tft import tracker, game


def generate_file_name():
    import time
    ts = time.time()
    return "test/{}.json".format(str(int(ts)))


def main():
    screenshot = True
    debug = True

    gameWindow = game.wait_for_game_to_begin(screenshot)
    gameBoard = game.initialize_game_board(gameWindow)

    players = game.retrieve_player_list(gameWindow, gameBoard) if not screenshot else []

    file_name = generate_file_name() if not debug else None
    gameTracker = tracker.Tracker(players, file_name=file_name)

    game.track_game(gameWindow, gameBoard, gameTracker, debug=debug)


main()
