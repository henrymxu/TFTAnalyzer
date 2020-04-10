from tft import tracker, game


def main():
    screenshot = True

    gameWindow = game.wait_for_game_to_begin(screenshot)
    gameBoard = game.initialize_game_board(gameWindow)

    players = game.retrieve_player_list(gameWindow, gameBoard) if not screenshot else []
    gameTracker = tracker.Tracker(players)

    game.track_game(gameWindow, gameBoard, gameTracker, debug=True)


main()
