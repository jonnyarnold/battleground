import unittest
import battleground_engine as bg

class TestGame(unittest.TestCase):
  def test_game_initialisation_with_default_window(self):
    game = bg.Battleground((bg.WIDTH,bg.HEIGHT))
