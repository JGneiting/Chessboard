import RPi.GPIO as GPIO
import BoardFiles as BoardManagement
from BoardFiles.ChessBoard import Board
from GameFiles.ChessPieces import Pawn


BoardManagement.set_12v(True)
board = Board(17, 27)

# magnet.pulse(45)

run = True
while run:
    source = input("Input Square")
    temp = Pawn((0, 0), source, "White", None)
    board.capture(temp)
    run = "n" != input("Continue? (y/n): ")

GPIO.cleanup()
