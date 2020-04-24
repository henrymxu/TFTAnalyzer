import multiprocessing

from tft import utils


class Tracker:
    def __init__(self, players, file_name=None):
        self.__unitLookupTable = initialize_unit_lookup_table()
        manager = multiprocessing.Manager()
        self.__stages = manager.dict()
        self.__current_stage = "0-0"
        self.__players = players
        self.__file_name = file_name
        if file_name:
            utils.create_json_array_file(self.__file_name)

        ctx = multiprocessing.get_context('spawn')
        self.__entry_queue = ctx.SimpleQueue()
        self.__process = ctx.Process(target=self.addEntries)

    def track(self):
        self.__process.start()

    def getEntryQueue(self):
        return self.__entry_queue

    def getStages(self):
        return self.__stages

    def writeToFile(self):
        self.__entry_queue.put({"mode": "finish", "contents": {"stage": "0-0"}})
        self.__process.join()
        if self.__file_name:
            utils.append_to_json_array_file(self.__file_name, self.__stages.copy())

    def hasStageChanged(self, stage):
        """
        Determines whether or not the stage has changed.

        If the stage has changed, the current stage is updated

        :param stage: string with format (x-y)
        :return: boolean
        """
        result = self.__current_stage != stage
        if result:
            self.__current_stage = stage
            self.createStageIfNeeded(stage)
        return result

    def addEntries(self):
        while True:
            data = self.__entry_queue.get()
            stage = data["contents"]["stage"]
            if stage == "0-0":
                break
            self.createStageIfNeeded(stage)
            if data["mode"] == "shop":
                units = data["contents"]["units"]
                level = data["contents"]["level"]
                gold = data["contents"]["gold"]
                self.addShop(stage, units, level, gold)
            elif data["mode"] == "healthbars":
                healthbars = data["contents"]["healthbars"]
                self.addHealthbars(stage, healthbars)

    def addHealthbars(self, stage, healthbars):
        if self.__players:
            players = {}
            for player, health in healthbars:
                matched_player = utils.find_matching_string_in_list(player, self.__players, 80)
                if matched_player == "" and player.isdigit():
                    players[""] = player
                players[matched_player] = health
        else: # Should never happen
            players = dict(healthbars)
        temp_dict = self.__stages[stage].copy()
        temp_dict["players"] = players
        self.__stages[stage] = temp_dict

    def addShop(self, stage, units, level, gold):
        """
        Add a shop to the tracker if has yet to be added, along with the current level and gold amount.

        :param units: list of un-processed units
        :param stage:
        :param level:
        :param gold:
        :return: boolean
        """
        units = [utils.find_matching_string_in_list(i, self.__unitLookupTable, 75) for i in units]
        shop = _create_shop(units, level, gold)
        temp_dict = self.__stages[stage].copy()
        temp_dict["shops"].append(shop)
        self.__stages[stage] = temp_dict

    def createStageIfNeeded(self, stage):
        if stage in self.__stages:
            return
        self.__stages[stage] = {"shops": []}


def _create_shop(units, level, gold):
    return {"units": units, "level": level, "gold": gold}


def _create_stage(stage, healthbars, level, gold):
    return {"stage": stage, "healthbars": healthbars, "level": level, "gold": gold, "shops": []}


def initialize_unit_lookup_table():
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
