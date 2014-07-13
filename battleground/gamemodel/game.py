"""
Game flow and rule container
"""
class Game:

    """
    Constructor. Takes two Player objects
    """
    def __init__(self, player1, player2):
        self.players = [player1, player2]
