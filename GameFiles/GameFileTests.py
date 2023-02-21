import unittest
from GameFiles.StateManager import ChessLogic, Simulator
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


class CheckLogic(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
