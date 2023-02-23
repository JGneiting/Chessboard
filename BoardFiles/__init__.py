import RPi.GPIO as GPIO
from BoardFiles.ChessBoard import Board


def get_board():
    set_5v(True)
    set_12v(True)
    return Board(magnet_pull, magnet_push)

def set_5v(state):
    GPIO.output(v5_pin, state)

def set_12v(state):
    GPIO.output(v12_pin, state)

v12_pin = 22
v5_pin = 6
magnet_pull = 17
magnet_push = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(v12_pin, GPIO.OUT)
GPIO.setup(v5_pin, GPIO.OUT)
GPIO.setup(magnet_pull, GPIO.OUT)
GPIO.setup(magnet_push, GPIO.OUT)

# GPIO.output(magnet_pull, 0)
# GPIO.output(magnet_push, 0)
# GPIO.output(v12_pin, 1)
# GPIO.output(v5_pin, 1)




