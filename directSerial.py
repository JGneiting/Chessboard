import RPi.GPIO as GPIO
import BoardFiles as BoardManagement
from BoardFiles.MotorManager import SerialAxis
from BoardFiles.MagnetManager import Magnet


# board = BoardManagement.get_board()

# invert = "y" == input("Invert Board? (y/n): ")
# if invert:
#     board.invert()

# board.move_between("A1", "B3", 2)

BoardManagement.set_12v(True)
axis = SerialAxis()
magnet = Magnet(17, 27)
# magnet.pulse(45)
axis.init_motors()

run = True
while run:
    source = input("Source: ")
    dest = input("Destination: ")
    axis.synchronized_move(float(source), float(dest), 1)
    axis.write_queue()
    run = "n" != input("Continue? (y/n): ")

magnet.deactivate()
GPIO.cleanup()
