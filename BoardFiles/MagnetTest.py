import RPi.GPIO as GPIO
from BoardFiles.MotorManager import DualAxis
from BoardFiles.MagnetManager import Magnet
from time import sleep


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

sleep(5)

magnet = Magnet(magnet_pull, magnet_push)
magnet.activate(push=True)
sleep(5)
magnet.deactivate()

GPIO.output(v12_pin, 0)
GPIO.output(v5_pin, 0)

GPIO.cleanup()