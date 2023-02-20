import RPi.GPIO as GPIO
from BoardFiles.ChessBoard import Board


v12_pin = 22
v5_pin = 6
magnet_pull = 17
magnet_push = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(v12_pin, GPIO.OUT)
GPIO.setup(v5_pin, GPIO.OUT)
GPIO.setup(magnet_pull, GPIO.OUT)
GPIO.setup(magnet_push, GPIO.OUT)

GPIO.output(magnet_pull, 0)
GPIO.output(magnet_push, 0)
GPIO.output(v12_pin, 1)
GPIO.output(v5_pin, 1)

board = Board(magnet_pull, magnet_push)

run = True
invert = "y" == input("Invert Board? (y/n): ")
if invert:
    board.invert()



while run:
    source = input("Source: ")
    dest = input("Destination: ")
    board.move_piece(source, dest, 2)
    run = "n" != input("Continue? (y/n): ")

board.close()

GPIO.cleanup()
