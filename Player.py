'''
Created on Oct 24, 2017

@author: Furkan Arslan
'''

from Board import Board

class Player:
    """
    A class to be inherited by any class representing a checkers player.
    This is used so that other functions can be written for more general use,
    without worry of crashing (e.g. play_n_games).
    
    NOTES:
    1) Create set playerID method
    """

    def set_board(self, the_board):
        """
        Sets the Board object which is known by the AI.
        """
        self.board = the_board
    
    def game_completed(self):
        """
        Should be overridden if AI implementing this class should be notified 
        of when a game ends, before the board is wiped.
        """
        pass
    
    def get_next_move(self):
        """
        Gets the desired next move from the AI.
        """
        pass