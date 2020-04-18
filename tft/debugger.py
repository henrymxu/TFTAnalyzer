from queue import Queue, PriorityQueue

from tft import image_utils

PlayerWindowOverlay = "player_overlay"
WindowOverly = "window_overlay"
ParseGold = "parse_gold"
ParseStage = "parse_stage"
ParseLevel = "parse_level"
ParseShop = "parse_shop"
ParseHealthbars = "parse_healthbars"
ParsePlayers = "parse_players"


class Debugger:
    def __init__(self):
        self.__display_queue = PriorityQueue()
        self.__hide_queue = Queue()
        self.__debuggable_functions = {}

    def enable_all(self):
        self.enable_window_overlay()
        self.enable_player_window_overlay()
        self.enable_parse_gold()
        self.enable_parse_stage()
        self.enable_parse_level()
        self.enable_parse_shop()
        self.enable_parse_healthbars()
        self.enable_parse_players()

    def enable_window_overlay(self):
        self.__debuggable_functions[WindowOverly] = True

    def enable_player_window_overlay(self):
        self.__debuggable_functions[PlayerWindowOverlay] = True

    def enable_parse_gold(self):
        self.__debuggable_functions[ParseGold] = True

    def enable_parse_stage(self):
        self.__debuggable_functions[ParseStage] = True

    def enable_parse_level(self):
        self.__debuggable_functions[ParseLevel] = True

    def enable_parse_shop(self):
        self.__debuggable_functions[ParseShop] = True

    def enable_parse_healthbars(self):
        self.__debuggable_functions[ParseHealthbars] = True

    def enable_parse_players(self):
        self.__debuggable_functions[ParsePlayers] = True

    def add_window(self, img, window_name, function):
        """
        Add a window to be shown by the debugger.

        :param img:
        :param window_name:
        :param function:
        :return:
        """
        if function in self.__debuggable_functions:
            size = len(img)
            tiebreaker = self.__display_queue.qsize()
            self.__display_queue.put((-size, tiebreaker, (img, window_name)))

    def show(self):
        """
        Show all windows in the queue after closing the previously shown ones.

        Windows are shown with larger windows behind smaller windows.
        :return:
        """
        while True:
            if self.__hide_queue.empty():
                break
            window_name = self.__hide_queue.get(block=False)
            image_utils.close_window(window_name)

        while True:
            if self.__display_queue.empty():
                break
            _, _, res = self.__display_queue.get(block=False)
            img = res[0]
            window_name = res[1]
            if img is None or window_name is None:
                break
            image_utils.show_image(img, window_name)
            self.__display_queue.task_done()
            self.__hide_queue.put(window_name)

        image_utils.wait()
