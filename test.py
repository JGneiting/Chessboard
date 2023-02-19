import RPi.GPIO as GPIO
from time import sleep


def alert(channel):
    print("\nEvent on channel " + str(channel))


GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(13, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)

GPIO.output(6, 0)
GPIO.output(12, 1)
GPIO.add_event_detect(23, GPIO.FALLING, callback=alert, bouncetime=250)
GPIO.add_event_detect(24, GPIO.FALLING, callback=alert, bouncetime=250)
GPIO.add_event_detect(25, GPIO.FALLING, callback=alert, bouncetime=250)
GPIO.add_event_detect(5, GPIO.FALLING, callback=alert, bouncetime=250)

GPIO.output(13, 0)
GPIO.output(16, 0)

GPIO.output(26, 0)
GPIO.output(21, 0)

delay = .005
for i in range(200):
    GPIO.output(19, 1)
    GPIO.output(20, 1)
    sleep(delay)
    GPIO.output(19, 0)
    GPIO.output(20, 0)
    sleep(delay)

message = input("\nPress any key to exit.\n")

GPIO.cleanup()
