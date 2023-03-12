from GameFiles.StateManager import ChessLogic
from GameFiles.ChessPieces import *


class TestBoard(ChessLogic):
    def __init__(self, single_team=False, upgrade_interface=False):
        super().__init__()
        self.single = single_team
        self.upgrade = upgrade_interface
        self.upgrade_name = ""

        self.board = [[None]*8 for i in range(8)]

    def run_stalemate_test(self):
        if not self.single:
            super().run_stalemate_test()

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

    def set_upgrade_piece(self, name):
        self.upgrade_name = name

    def get_pawn_upgrade(self, pawn):
        if self.upgrade:
            super().upgrade_pawn(pawn, self.upgrade_name)
        else:
            super().get_pawn_upgrade(pawn)


