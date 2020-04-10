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


class TestTracker(unittest.TestCase):
    def test_addStage(self):
        subject = tracker.Tracker(generate_player_list(), False)
        subject.addStage("2-1", generate_health_bars(), 3, 10)

        subject.addShopIfChanged(generate_shop_1(), 3, 10)
        subject.addShopIfChanged(generate_shop_2(), 3, 8)

        subject.addStage("2-2", generate_health_bars(), 4, 5)


if __name__ == '__main__':
    unittest.main()
