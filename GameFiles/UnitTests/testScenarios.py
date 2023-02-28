import unittest
from GameFiles.UnitTests import TestBoard
from GameFiles.ChessErrors import *


class ExtendedCheckTest(unittest.TestCase):

    def test_multi_blocking(self):
        board = TestBoard()
        queenW = board.create_piece("C3", "Queen")
        pawnW = board.create_piece("E5", "Pawn")
        kingW = board.create_piece("E1", "King")
        bishopW = board.create_piece("F1", "Bishop")
        knightW1 = board.create_piece("F3", "Knight")
        knightW2 = board.create_piece("G1", "Knight")

        queenB = board.create_piece("E8", "Queen", "Black")
        kingB = board.create_piece("D8", "King", "Black")
        knightB = board.create_piece("C6", "Knight", "Black")

        board.turn = "Black"

        self.assertIn("E5", queenB.get_possible_moves())
        self.assertIn("E5", knightB.get_possible_moves())

        board.move_piece("E8", "E5")
        self.assertTrue(board.in_check)

        self.assertEqual(["E5"], knightW1.get_possible_moves())
        self.assertEqual(["E2"], bishopW.get_possible_moves())
        self.assertEqual(["E2"], knightW2.get_possible_moves())
        self.assertEqual(["E3", "E5"], queenW.get_possible_moves())
        self.assertEqual(["F2", "D2", "D1"], kingW.get_possible_moves())

        board.move_piece("C3", "E5")
        self.assertFalse(board.in_check)

        self.assertIn("E5", knightB.get_possible_moves())

