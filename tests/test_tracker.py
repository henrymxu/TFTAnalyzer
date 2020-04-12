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

    def test_addStage(self):
        subject = tracker.Tracker(generate_player_list())
        subject.addStage("2-1", generate_health_bars(), 3, 10)

        subject.addShopIfChanged(generate_shop_1(), "2-1", 3, 10)
        subject.addShopIfChanged(generate_shop_2(), "2-1", 3, 8)

        subject.addStage("2-2", generate_health_bars(), 4, 5)

        subject.addShopIfChanged(generate_shop_3(), "2-2", 3, 15)
        subject.addShopIfChanged(generate_shop_1(), "2-2", 4, 8)

        result = subject.getStages()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["stage"], "2-1")
        self.assertEqual(result[1]["stage"], "2-2")


if __name__ == '__main__':
    unittest.main()
