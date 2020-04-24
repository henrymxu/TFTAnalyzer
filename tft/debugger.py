import multiprocessing

from tft import image_utils, utils

PlayerWindowOverlay = "player_overlay"
WindowOverly = "window_overlay"
ParseGold = "parse_gold"
ParseStage = "parse_stage"
ParseLevel = "parse_level"
ParseShop = "parse_shop"
ParseHealthbars = "parse_healthbars"
ParsePlayers = "parse_players"
ParseCircles = "parse_circles"


class Debugger:

    def __init__(self):
        self.__is_attached = False
        self.__wait = 25

        self.__debuggable_functions = multiprocessing.Manager().dict()
        ctx = multiprocessing.get_context('spawn')
        self.__display_queue = ctx.Queue()
        self.__hide_queue = ctx.Queue()

    def validation_mode(self):
        self.__wait = 0

    def enable_all(self):
        self.enable_window_overlay()
        self.enable_player_window_overlay()
        self.enable_parse_gold()
        self.enable_parse_stage()
        self.enable_parse_level()
        self.enable_parse_shop()
        self.enable_parse_circles()
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

    def enable_parse_circles(self):
        self.__debuggable_functions[ParseCircles] = True

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
        not_ready_to_hide_list = []
        while not self.__hide_queue.empty():
            window_name, time = self.__hide_queue.get(block=False)
            if utils.end_timer(time) <= 5:
                not_ready_to_hide_list.append((window_name, time))
            else:
                image_utils.close_window(window_name)

        for not_ready_to_hide in not_ready_to_hide_list:
            self.__hide_queue.put(not_ready_to_hide)

        while not self.__display_queue.empty():
            _, _, res = self.__display_queue.get(block=False)
            img = res[0]
            window_name = res[1]
            if img is None or window_name is None:
                break
            image_utils.show_image(img, window_name, wait_key_delay=self.__wait)
            self.__hide_queue.put((window_name, utils.start_timer()))

        image_utils.wait()
