import RPi.GPIO as GPIO
import BoardFiles as BoardManagement
from BoardFiles.ChessBoard import Board
from GameFiles.ChessPieces import Pawn, Rook


BoardManagement.set_12v(True)
board = Board(17, 27)

# magnet.pulse(45)

run = True
i = 0
teams = ["White", "Black"]
while run:
    source = input("Source: ")
    dest = input("Dest: ")
    # if (i/2) % 2 == 0:
    #     piece = Pawn(source, source, teams[i%2], None)
    # else:
    #     piece = Rook(source, source, teams[i%2], None)
    # board.capture(piece)
    board.move_piece(source, dest, 1)
    run = "n" != input("Continue? (y/n): ")
    i += 1

GPIO.cleanup()
