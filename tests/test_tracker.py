import unittest

from tft import tracker


def generate_player_list():
    return "player1", "player2", "player3", "player4", "player5", "player6", "player7", "player8"


def generate_health_bars():
    return ("player1", "100"), ("player2", "100"), ("player3", "100"), ("player4", "100"), ("player5", "100"), \
           ("player6", "100"), ("player7", "100"), ("player8", "100")


def generate_shop_1():
    return "Ahri", "Syndra", "Neeko", "Poppy", "Zoe"


def generate_shop_2():
    return "Lucian", "Fiora", "Leona", "Vi", "Irelia"


def generate_shop_3():
    return "Shaco", "Jhin", "Karma", "Lux", "Mordekaiser"


class TestTracker(unittest.TestCase):

    def setUp(self):
        self.subject = tracker.Tracker(generate_player_list())

    def test_addStage(self):
        self.subject.hasStageChanged("2-1")

        self.subject.addShop("2-1", generate_shop_1(), 3, 10)
        self.subject.addShop("2-1", generate_shop_1(), 3, 8)

        self.subject.hasStageChanged("2-2")

        self.subject.addShop("2-2", generate_shop_3(), 3, 15)
        self.subject.addShop("2-2", generate_shop_1(), 4, 8)

        result = self.subject.getStages()
        self.assertEqual(len(result), 2)
        self.assertTrue("2-1" in result)
        self.assertTrue("2-2" in result)
        self.assertEqual(len(result["2-1"]["shops"]), 2)

    def test_addShop(self):
        self.subject.hasStageChanged("2-1")
        self.subject.addShop("2-1", ["a", "b", "c", "d", "e"], 8, 10)
        result = self.subject.getStages()
        self.assertEqual(result["2-1"]["shops"][0]["gold"], 10)
        self.subject.addShop("2-1", ["Shako", "Jhln", "Karwa", "Lux", "Moredkalser"], 8, 10)
        result = self.subject.getStages()
        equal = all([i == j for i, j in zip(generate_shop_3(), result["2-1"]["shops"][0]["units"])])
        self.assertTrue(equal)


if __name__ == '__main__':
    unittest.main()
