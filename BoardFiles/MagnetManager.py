import RPi.GPIO as GPIO


class Magnet:

    def __init__(self, pull_pin, push_pin):
        self.pull = pull_pin
        self.push = push_pin

        GPIO.output(self.pull, 0)
        GPIO.output(self.push, 0)

    def activate(self, push=False):
        if push:
            GPIO.output(self.pull, 0)
            GPIO.output(self.push, 1)
        GPIO.output(self.push, 0)
        GPIO.output(self.pull, 1)

    def deactivate(self):
        GPIO.output(self.pull, 0)
        GPIO.output(self.push, 0)