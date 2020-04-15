from fuzzywuzzy import process, fuzz

from tft import utils


class Tracker:
    def __init__(self, players, file_name=None):
        self.__unitLookupTable = self._initializeUnitLookupTable()
        self.__lastShop = {}
        self.__stages = []
        self.__players = players
        if file_name:
            self.__file_name = file_name
            utils.create_json_array_file(self.__file_name)

    def _initializeUnitLookupTable(self):
        """
        Initialize the unit lookup table using json file provided from Riot (supports Set2 and Set3)

        :return:
        """
        unit_lookup_table = []
        json = utils.open_json_file("data/champions_set3.json")
        for unit in json:
            key = "name"  # Set 3 key
            if key not in unit:
                key = "champion"  # Set 2 key
            unit_lookup_table.append(unit[key])
        return unit_lookup_table

    def _findMatchingStringInList(self, string, list, score):
        """
        Attempts to match a string to an element in a list

        Uses Fuzzy string matching in order to find the correct string.  If the best match has a score lower than
        than the score provided, a blank string will be returned instead.

        :param string:
        :param list:
        :param score:
        :return:
        """
        import fuzzywuzzy.utils
        if string == "" or string == "Be":  # Weird case where empty shop tile appears as "Be"
            return ""
        string = fuzzywuzzy.utils.full_process(string)
        choice = process.extract(string, list, limit=1, scorer=fuzz.QRatio)
        if not choice or choice[0][1] < score:
            # print("Not a Match: {} != {}, score = {}".format(unit, choice[0][0], choice[0][1]))
            return ""
        # print("Found Match: {} == {}, score = {}".format(unit, choice[0][0], choice[0][1]))
        return choice[0][0]

    def getStages(self):
        return self.__stages

    def writeToFile(self):
        if self.__file_name:
            utils.append_to_json_array_file(self.__file_name, self.__stages)

    def hasShopChanged(self, units):
        """
        Determines whether or not the shop has changed.

        New shop items are compared to the previous shop items.  If 2 or more slots have different units,
        then the shop is considered changed.

        TODO: check gold/stage?

        :param units: list of post-processed units (validated and corrected with UnitLookupTable)
        :return: boolean
        """
        units_changed = 0
        for i in range(0, 5):
            if units[i] == "":
                continue
            if not self.__lastShop:
                return True
            if not self.__lastShop["units"][i] == units[i]:
                units_changed += 1
        return units_changed > 1

    def hasStageChanged(self, stage):
        """
        Determines whether or not the stage has changed.

        :param stage: string with format (x-y)
        :return: boolean
        """
        if self.__stages and self.__stages[-1]["stage"] == stage:
            return False
        return True

    def addStage(self, stage, healthbars, level, gold):
        if self.__players:
            players = {}
            for player, health in healthbars:
                player = self._findMatchingStringInList(player, self.__players, 80)
                players[player] = health
        else:
            players = dict(healthbars)
        self.__stages.append(_create_stage(stage, players, level, gold))

    def addShopIfChanged(self, units, stage, level, gold):
        """
        Add a shop to the tracker if has yet to be added, along with the current level and gold amount.

        :param units: list of un-processed units
        :param level:
        :param gold:
        :return: boolean
        """
        units = [self._findMatchingStringInList(i, self.__unitLookupTable, 75) for i in units]
        if not self.hasShopChanged(units):
            return False
        shop = _create_shop(units, level, gold)
        self._addShopToStage(stage, shop)
        self.__lastShop = shop
        return True

    def _addShopToStage(self, stage, shop):
        saved_stage = next(search for search in self.__stages if search["stage"] == stage)
        saved_stage["shops"].append(shop)


def _create_shop(units, level, gold):
    return {"units": units, "level": level, "gold": gold}


def _create_stage(stage, healthbars, level, gold):
    return {"stage": stage, "healthbars": healthbars, "level": level, "gold": gold, "shops": []}
