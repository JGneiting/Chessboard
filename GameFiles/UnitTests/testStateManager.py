import unittest
from GameFiles.UnitTests import TestBoard
from GameFiles.StateManager import Simulator
from GameFiles.ChessErrors import *


class CheckLogic(unittest.TestCase):
    def test_pawn_blocking(self):
        board = TestBoard()
        pawn = board.create_piece("B2", "Pawn")
        board.create_piece("C1", "Bishop")
        board.create_piece("D1", "King")
        board.create_piece("D2", "Pawn")
        board.create_piece("E2", "Pawn")
        board.create_piece("E1", "Queen")
        board.create_piece("E8", "Queen", "Black")

        board.turn = "Black"
        board.move_piece("E8", "A4")

        moves = pawn.get_possible_moves()
        self.assertNotIn("B4", moves)

    def test_moves_square(self):
        board = TestBoard()
        board.create_piece("A2", "Pawn")

        moves = board.get_valid_moves("A2")
        self.assertEqual(["A3", "A4"], moves)

        moves = board.get_valid_moves("A5")
        self.assertEqual([], moves)

    def test_getting_team_pieces(self):
        board = TestBoard()
        p1 = board.create_piece("A2", "Pawn")
        p2 = board.create_piece("A3", "Pawn")

        pieces = board.get_team_pieces("White")
        self.assertEqual([p1, p2], pieces)

    def test_detection(self):
        board = TestBoard()
        board.create_piece("A1", "Rook")
        board.create_piece("A8", "King", "Black")

        board.run_check_cycle()
        self.assertEqual(True, board.checked("Black"))

    def test_detection_on_move(self):
        board = TestBoard()
        board.create_piece("B1", "Rook")
        board.create_piece("A8", "King", "Black")

        board.run_check_cycle()
        self.assertEqual(False, board.checked("Black"))
        board.move_piece("B1", "A1")
        self.assertEqual(True, board.checked("Black"))

    def test_valid_moves_in_check(self):
        board = TestBoard()
        king = board.create_piece("D1", "King")
        board.create_piece("A1", "Rook", "Black")

        board.turn = "Black"
        board.run_check_cycle()
        board.turn = "White"
        moves = king.get_possible_moves()
        self.assertEqual(["E2", "D2", "C2"], moves)

    def test_blocking_moves_in_check(self):
        board = TestBoard()
        bishop = board.create_piece("C2", "Bishop")
        board.create_piece("D1", "King")
        board.create_piece("A1", "Rook", "Black")

        board.turn = "Black"
        board.run_check_cycle()
        board.turn = "White"
        moves = bishop.get_possible_moves()
        self.assertEqual(["B1"], moves)

    def test_killing_aggressor(self):
        board = TestBoard()
        bishop = board.create_piece("B2", "Bishop")
        board.create_piece("D1", "King")
        board.create_piece("A1", "Rook", "Black")

        board.turn = "Black"
        board.run_check_cycle()
        board.turn = "White"
        moves = bishop.get_possible_moves()
        self.assertEqual(["A1", "C1"], moves)

        board = TestBoard()
        king = board.create_piece("A1", "King")
        board.create_piece("A3", "Queen", "Black")
        board.create_piece("B1", "Rook", "Black")
        moves = king.get_possible_moves()
        self.assertEqual(["B1"], moves)

        board.turn = "Black"
        board.move_piece("A3", "C1")
        moves = king.get_possible_moves()
        self.assertEqual(["A2"], moves)

    def test_moving_in_check(self):
        board = TestBoard()
        king = board.create_piece("D1", "King")
        board.create_piece("A2", "Rook", "Black")

        moves = king.get_possible_moves()
        self.assertEqual(["E1", "C1"], moves)

    def test_moving_protection(self):
        board = TestBoard()
        rook = board.create_piece("C1", "Rook")
        board.create_piece("D1", "King")
        board.create_piece("A1", "Rook", "Black")

        moves = rook.get_possible_moves()
        self.assertEqual(["B1", "A1"], moves)

    def test_checkmate_detection(self):
        board = TestBoard()
        board.create_piece("C3", "Queen")
        board.create_piece("D7", "Rook")
        board.create_piece("A8", "King", "Black")

        with self.assertRaises(Checkmate):
            board.move_piece("C3", "C8")


class SimulatorIndependance(unittest.TestCase):
    def test_proper_copy(self):
        source = TestBoard()
        source.create_piece("A3", "Pawn")

        test = Simulator(source)
        self.assertNotEqual(source, test)
        self.assertEqual(str(source), str(test))

    def test_pawn_upgrading_ignored(self):
        board = TestBoard()
        pawn = board.create_piece("A7", "Pawn")

        pawn.get_possible_moves()

    def test_independance(self):
        source = TestBoard()
        src_pawn = source.create_piece("A3", "Pawn")

        test = Simulator(source)
        test.move_piece("A3", "A4")
        self.assertNotEqual(source, test)
        self.assertNotEqual(str(source), str(test))
        self.assertEqual("Pawn", str(source.get_square("A3")))
        self.assertEqual("Pawn", str(test.get_square("A4")))
        moves = src_pawn.get_possible_moves()
        self.assertEqual(["A4", "A5"], moves)
        self.assertEqual("Pawn", str(source.get_square("A3")))
        self.assertEqual("Pawn", str(test.get_square("A4")))


class GameFlowTests(unittest.TestCase):
    def test_turn_tracking(self):
        board = TestBoard()
        white = board.create_piece("A1", "Rook")
        black = board.create_piece("H8", "Rook", "Black")

        with self.assertRaises(TurnError):
            board.move_piece("H8", "A8")
        board.move_piece("A1", "D1")
        with self.assertRaises(TurnError):
            board.move_piece("D1", "A1")
        board.move_piece("H8", "A8")
        self.assertEqual("D1", white.get_location())
        self.assertEqual("A8", black.get_location())

    def test_invalid_move_entry(self):
        board = TestBoard()
        board.create_piece("C3", "Pawn")

        with self.assertRaises(InvalidMove):
            board.move_piece("C3", "C2")

    def test_out_of_bounds_entry(self):
        board = TestBoard()
        board.create_piece("C3", "Pawn")

        with self.assertRaises(UnknownSquare):
            board.move_piece("Q3", "C0")
