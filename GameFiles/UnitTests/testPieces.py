import unittest
from GameFiles.UnitTests import TestBoard
from GameFiles.ChessErrors import PawnUpgrade
from GameFiles.ChessPieces import Piece


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

        self.assertEqual([], moves)

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

        board = TestBoard(True)
        rook = board.create_piece("D4", "Rook")
        moves = rook.get_possible_moves()
        self.assertEqual(["E4", "F4", "G4", "H4", "D5", "D6", "D7", "D8", "C4", "B4", "A4", "D3", "D2", "D1"], moves)

    def test_blocked_path(self):
        board = TestBoard(True)
        rook = board.create_piece("A1", "Rook")
        board.create_piece("C1", "Rook")
        board.create_piece("A3", "Rook", "Black")

        moves = rook.get_possible_moves()
        self.assertEqual(["B1", "A2", "A3"], moves)


class BishopTest(unittest.TestCase):
    def test_unobstructed(self):
        board = TestBoard(True)
        bishop = board.create_piece("A1", "Bishop")

        moves = bishop.get_possible_moves()
        self.assertEqual(["B2", "C3", "D4", "E5", "F6", "G7", "H8"], moves)

        board = TestBoard(True)
        bishop = board.create_piece("D4", "Bishop")
        moves = bishop.get_possible_moves()
        self.assertEqual(["E5", "F6", "G7", "H8", "C5", "B6", "A7", "C3", "B2", "A1", "E3", "F2", "G1"], moves)

    def test_obstructed(self):
        board = TestBoard(True)
        bishop = board.create_piece("B2", "Bishop")
        board.create_piece("A1", "Knight", "Black")
        board.create_piece("C3", "Rook")

        moves = bishop.get_possible_moves()
        self.assertEqual(["A3", "A1", "C1"], moves)


class TestKnight(unittest.TestCase):
    def test_base_locations(self):
        board = TestBoard(True)
        knight = board.create_piece("A1", "Knight")
        moves = knight.get_possible_moves()
        self.assertEqual(["B3", "C2"], moves)

        board = TestBoard(True)
        knight = board.create_piece("D4", "Knight")
        moves = knight.get_possible_moves()
        self.assertEqual(['E6', 'F5', 'C6', 'F3', 'E2', 'B5', 'C2', 'B3'], moves)

    def test_obstructed(self):
        board = TestBoard(True)
        knight = board.create_piece("A1", "Knight")
        board.create_piece("B3", "Pawn")
        board.create_piece("C2", "Pawn", "Black")
        moves = knight.get_possible_moves()
        self.assertEqual(["C2"], moves)