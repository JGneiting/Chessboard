import RPi.GPIO as GPIO
import time


class Magnet:

    def __init__(self, pull_pin, push_pin):
        self.pull = pull_pin
        self.push = push_pin

        GPIO.output(self.pull, 0)
        GPIO.output(self.push, 0)
        self.pull_pin = GPIO.PWM(self.pull, 50)
        self.push_pin = GPIO.PWM(self.push, 50)

    def activate(self, push=False):
        if push:
            self.pull_pin.stop()
            time.sleep(0.1)
            self.push_pin.start(100)
        else:
            self.push_pin.stop()
            time.sleep(0.1)
            self.pull_pin.start(100)

    def set_duty_cycle(self, duty_cycle):
        self.pull_pin.ChangeDutyCycle(duty_cycle)
        self.push_pin.ChangeDutyCycle(duty_cycle)

    def deactivate(self):
        self.pull_pin.stop()
        self.push_pin.stop()

    def pulse(self, duty_cycle, push=False):
        if push:
            self.pull_pin.stop()
            time.sleep(0.1)
            self.push_pin.start(duty_cycle)
        else:
            self.push_pin.stop()
            time.sleep(0.1)
            self.pull_pin.start(duty_cycle)
