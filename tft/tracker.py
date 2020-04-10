import time

from fuzzywuzzy import process, fuzz

from tft import utils

_FileLocation = "test/{}.json"


class Tracker:
    def __init__(self, players, write=True):
        self.__unitLookupTable = self._initializeUnitLookupTable()
        self.__shops = []
        self.__state = {}
        self.__players = players
        self.__write = write
        if write:
            ts = time.time()
            self.__fileName = _FileLocation.format(str(int(ts)))
            utils.create_json_array_file(self.__fileName)

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

    def _findUnitInLookupTable(self, unit):
        """
        Attempts to find unit in lookup table

        Uses Fuzzy string matching in order to find the correct unit.  If the best match has a score lower than
        75, a blank string will be returned instead.

        :param unit: post processed string representing a unit
        :return: string
        """
        if unit == "" or unit == "Be":  # Weird case where empty shop tile appears as "Be"
            return ""
        choice = process.extract(unit, self.__unitLookupTable, limit=1, scorer=fuzz.QRatio)
        if choice[0][1] <= 75:
            # print("Not a Match: {} != {}, score = {}".format(unit, choice[0][0], choice[0][1]))
            return ""
        # print("Found Match: {} == {}, score = {}".format(unit, choice[0][0], choice[0][1]))
        return choice[0][0]

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
            if not self.__shops:
                return True
            if not self.__shops[-1]["units"][i] == units[i]:
                units_changed += 1
        return units_changed > 1

    def hasStageChanged(self, stage):
        """
        Determines whether or not the stage has changed.

        :param stage: string with format (x-y)
        :return: boolean
        """
        if self.__state and self.__state["stage"] and self.__state["stage"] == stage:
            return False
        return True

    def addStage(self, stage, healthbars, level, gold):
        if self.__state and self.__write:
            utils.append_to_json_file(self.__fileName, self.__state)
        self.__shops.clear()
        self.__state = _create_state(stage, healthbars, level, gold, self.__shops)

    def addShopIfChanged(self, units, level, gold):
        """
        Add a shop to the tracker if has yet to be added, along with the current level and gold amount.

        :param units: list of un-processed units
        :param level:
        :param gold:
        :return: boolean
        """
        units = [self._findUnitInLookupTable(i) for i in units]
        if not self.hasShopChanged(units):
            return False
        shop = _create_shop(units, level, gold)
        self.__shops.append(shop)
        return True


def _create_shop(units, level, gold):
    return {"units": units, "level": level, "gold": gold}


def _create_state(stage, healthbars, level, gold, shops):
    return {"stage": stage, "healthbars": healthbars, "level": level, "gold": gold, "shops": shops}
