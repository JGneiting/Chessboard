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
    x = float(input("X: "))
    y = float(input("Y: "))
    board.axis.synchronized_move(*board.convert_axes(x, y))
    board.axis.write_queue()
    run = "n" != input("Continue? (y/n): ")
    i += 1

GPIO.cleanup()
