from tft import game, utils, main

if __name__ == "__main__":
    gameWindow = game.wait_for_window_to_appear()
    file_name = f"test/{utils.generate_file_name()}"
    main.main(gameWindow, file_name=file_name)
