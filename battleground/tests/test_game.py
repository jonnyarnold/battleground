import unittest
from gamemodel import Game

class GameTests(unittest.TestCase):
  def test_game_requires_two_players(self):
    with self.assertRaises(Exception, msg="0 players allowed"):
      game = model.Game(None, None)
    
    with self.assertRaises(Exception, msg="1 player allowed"):
      game1 = model.Game(Player(), None)
      game2 = model.Game(None, Player())
    
    validGame = model.Game(Player(), Player())
    
    
