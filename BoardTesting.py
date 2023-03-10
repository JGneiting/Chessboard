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
    if (i/2) % 2 == 0:
        piece = Pawn(source, source, teams[i%2], None)
    else:
        piece = Rook(source, source, teams[i%2], None)
    board.capture(piece)
    run = "n" != input("Continue? (y/n): ")
    i += 1

GPIO.cleanup()
