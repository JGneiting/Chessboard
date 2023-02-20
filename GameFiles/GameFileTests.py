import unittest
from GameFiles.StateManager import ChessLogic
from GameFiles.ChessPieces import *
from GameFiles.ChessErrors import *


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


class PawnTests(unittest.TestCase):
    def test_forward_first(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        moves = pawn.get_possible_moves()

        self.assertEqual(["D3", "D4"], moves)  # add assertion here

    def test_forward_next(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        board.move_piece("D2", "D3")
        moves = pawn.get_possible_moves()

        self.assertEqual(["D4"], moves)  # add assertion here

    def test_left_capture(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        board.create_piece("C3", "Pawn", "Black")
        moves = pawn.get_possible_moves()

        self.assertEqual(["D3", "D4", "C3"], moves)

    def test_right_capture(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        board.create_piece("E3", "Pawn", "Black")
        moves = pawn.get_possible_moves()

        self.assertEqual(["D3", "D4", "E3"], moves)

    def test_both_capture(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        board.create_piece("C3", "Pawn", "Black")
        board.create_piece("E3", "Pawn", "Black")
        moves = pawn.get_possible_moves()

        self.assertEqual(["D3", "D4", "C3", "E3"], moves)

    def test_double_block(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        board.create_piece("D4", "Pawn", "Black")

        moves = pawn.get_possible_moves()

        self.assertEqual(["D3"], moves)

    def test_double_jump_block(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        board.create_piece("D3", "Pawn", "Black")

        moves = pawn.get_possible_moves()

        self.assertEqual([], moves)

    def test_team_capture(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        board.create_piece("C3", "Pawn", "Black")
        board.create_piece("E3", "Pawn")

        moves = pawn.get_possible_moves()

        self.assertEqual(["D3", "D4", "C3"], moves)

    def test_blocked_team_capture(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        board.create_piece("C3", "Pawn", "Black")
        board.create_piece("D4", "Pawn", "Black")
        board.create_piece("E3", "Pawn")

        moves = pawn.get_possible_moves()

        self.assertEqual(["D3", "C3"], moves)

    def test_forward_team_blocked(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        board.create_piece("C3", "Pawn", "Black")
        board.create_piece("D4", "Pawn")
        board.create_piece("E3", "Pawn")

        moves = pawn.get_possible_moves()

        self.assertEqual(["D3", "C3"], moves)

    def test_double_team_blocked(self):
        board = TestBoard(True)
        pawn = board.create_piece("D2", "Pawn")  # type: Piece
        board.create_piece("D3", "Pawn")
        board.create_piece("E3", "Pawn")

        moves = pawn.get_possible_moves()

        self.assertEqual(["C3"], moves)

    def test_board_edge(self):
        board = TestBoard(True)
        pawn = board.create_piece("A2", "Pawn")  # type: Piece
        board.create_piece("B3", "Pawn")
        board.create_piece("A3", "Pawn", "Black")

        moves = pawn.get_possible_moves()

        self.assertEqual([], moves)

    def test_upgrade_raised(self):
        board = TestBoard(True)
        pawn = board.create_piece("A8", "Pawn")  # type: Piece

        with self.assertRaises(PawnUpgrade):
            pawn.get_possible_moves()


class RookTests(unittest.TestCase):
    def test_unobstructed_path(self):
        board = TestBoard(True)
        rook = board.create_piece("A1", "Rook")

        moves = rook.get_possible_moves()
        self.assertEqual(["B1", "C1", "D1", "E1", "F1", "G1", "H1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"], moves)


if __name__ == '__main__':
    unittest.main()
