import RPi.GPIO as GPIO
import BoardFiles as BoardManagement


board = BoardManagement.get_board()

invert = "y" == input("Invert Board? (y/n): ")
if invert:
    board.invert()

board.move_between("A1", "B3", 2)

run = True
while run:
    source = input("Source: ")
    dest = input("Destination: ")
    board.move_piece(source, dest, 2)
    run = "n" != input("Continue? (y/n): ")

board.close()

GPIO.cleanup()
