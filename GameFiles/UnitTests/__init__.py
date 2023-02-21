import unittest
from GameFiles.StateManager import ChessLogic
from GameFiles.ChessPieces import *


class TestBoard(ChessLogic):
    def __init__(self, single_team=False):
        super().__init__()
        self.single = single_team

        self.board = [[None]*8 for i in range(8)]

    def initialize_board(self):
        pass

    def get_opposing_team(self, team):
        if self.single:
            return team
        else:
            return super().get_opposing_team(team)

    def create_piece(self, location, name, team="White"):
        piece = eval(f'{name}((0,0), location, team, self)')
        self.set_square(location, piece)
        return piece


import GameFiles.UnitTests.testPieces
import GameFiles.UnitTests.testStateManager

