import RPi.GPIO as GPIO
from time import sleep
from queue import Queue
from math import floor
import serial
import threading
import numpy as np


class MotorAxis:

    def __init__(self, enable_pin, step_pin, direction_pin, left_bumper_pin, right_bumper_pin):
        self.en_pin = enable_pin
        self.step_pin = step_pin
        self.dir_pin = direction_pin
        self.left_limit = left_bumper_pin
        self.right_limit = right_bumper_pin

        # TODO: Bouncetime should be able to be less, but the long wires may be overcoming the internal pull-up / bad
        #  connection
        self.homing_delay = .002
        self.min_delay = .0002
        self.bouncetime = 200

        GPIO.setup(self.en_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.left_limit, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.right_limit, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.position = None
        self.total_steps = None
        self.edge = None

        GPIO.add_event_detect(self.left_limit, GPIO.FALLING, callback=self.register_edge, bouncetime=self.bouncetime)
        GPIO.add_event_detect(self.right_limit, GPIO.FALLING, callback=self.register_edge, bouncetime=self.bouncetime)

        self.calibrate()

    def register_edge(self, channel):
        edge = 0
        if channel == self.right_limit:
            edge = 1
        self.edge = edge

    def calibrate(self):
        # Home the axis
        self.home()

        # Count steps to other side
        self.enable(True)
        self.edge = False
        steps = 0
        GPIO.output(self.dir_pin, 1)
        while self.edge != 1:
            GPIO.output(self.step_pin, 1)
            sleep(self.min_delay*3)
            GPIO.output(self.step_pin, 0)
            sleep(self.min_delay*3)
            steps += 1
        steps -= 200
        self.edge = None
        self.move(0, 200, self.homing_delay)
        sleep(.1)
        GPIO.output(self.dir_pin, 1)
        while self.edge != 1:
            GPIO.output(self.step_pin, 1)
            sleep(self.homing_delay)
            GPIO.output(self.step_pin, 0)
            sleep(self.homing_delay)
            steps += 1

        self.total_steps = steps
        print(steps)
        self.position = self.total_steps

        self.enable(False)

    def move(self, direction, steps, delay):
        print("Moving")
        delay = max(self.min_delay, delay)
        GPIO.output(self.dir_pin, direction)
        for i in range(steps):
            GPIO.output(self.step_pin, 1)
            sleep(delay)
            GPIO.output(self.step_pin, 0)
            sleep(delay)

    def move_to_edge(self, direction, delay):
        edge_pin = self.right_limit
        if direction == 0:
            edge_pin = self.left_limit
        if GPIO.input(edge_pin) == 0:
            self.move((direction+1 % 2), 400, delay)

        sleep(self.bouncetime / 1000)

        GPIO.output(self.dir_pin, direction)
        self.edge = None
        while self.edge != direction:
            GPIO.output(self.step_pin, 1)
            sleep(delay)
            GPIO.output(self.step_pin, 0)
            sleep(delay)

    def home(self):
        # Activate the driver
        self.enable(True)
        # Move carriage quickly to edge
        print("Quick Home")
        self.move_to_edge(0, self.min_delay*3)
        sleep(self.bouncetime/1000)
        print("Precise Home")
        self.move_to_edge(0, self.homing_delay)
        # Disable driver for power saving
        self.enable(False)

        # Set position variable
        self.position = 0

    def move_relative(self, position):
        print(position)
        if 0 <= position <= 1:
            print("Moving Axis")
            target = floor(self.total_steps * position)
            delta = target - self.position
            target_dir = 1
            if delta < 0:
                target_dir = 0
            delta = abs(delta)
            print(delta)
            self.enable(True)
            self.move(target_dir, delta, self.min_delay)
            self.enable(False)
            self.position = target

    def timed_move(self, direction, steps, total_time):
        total_time /= 2
        if steps != 0:
            step_delay = total_time / steps
            step_delay = max(step_delay, self.min_delay)
            step_delay -= steps * .000000011
            print(step_delay)
            self.move(direction, steps, step_delay)

    def timed_move_relative(self, position, total_time):
        print(position)
        if 0 <= position <= 1:
            print("Timed Move")
            target = floor(self.total_steps * position)
            delta = target - self.position
            target_dir = 1
            if delta < 0:
                target_dir = 0
            delta = abs(delta)
            print(delta)
            self.enable(True)
            self.timed_move(target_dir, delta, total_time)
            self.enable(False)
            self.position = target

    def enable(self, active):
        GPIO.output(self.en_pin, not active)


class ThreadedAxis(threading.Thread):

    def __init__(self, thread_id, name, counter, next_position, status, pin_data, my_lock, other_lock):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.queue = next_position
        self.status = status
        self.pin_data = pin_data
        self.my_lock = my_lock
        self.other_lock = other_lock

        self.axis = None
        self.my_lock.acquire()

    def run(self):
        pin_data = self.pin_data
        self.axis = MotorAxis(pin_data[0], pin_data[1], pin_data[2], pin_data[3], pin_data[4])
        self.status.put(0)
        self.status.put(self.axis.total_steps)

        msg_code = -1
        while msg_code != 0:
            if self.queue.qsize() < 1:
                sleep(.05)
            msg_code = self.queue.get()
            if msg_code == 1:
                print("Code 1")
                self.axis.move_relative(self.queue.get())
                self.status.put(1)
                self.status.put(1)
            if msg_code == 2:
                self.other_lock.release()
                self.my_lock.acquire()
                print("Code 2")
                position = self.queue.get()
                total_time = self.queue.get()
                self.axis.timed_move_relative(position, total_time)
                self.status.put(1)
                self.status.put(1)

        print("Motor Exiting")


class SerialAxis:

    def __init__(self):
        self.arduino = serial.Serial('/dev/ttyUSB0',
                                     baudrate=9600,
                                     bytesize=serial.EIGHTBITS,
                                     parity=serial.PARITY_NONE,
                                     stopbits=serial.STOPBITS_ONE,
                                     timeout=1,
                                     xonxoff=0,
                                     rtscts=0
                                     )
        # Toggle DTR to reset Arduino
        self.arduino.setDTR(False)
        sleep(1)
        # toss any data already received, see
        # http://pyserial.sourceforge.net/pyserial_api.html#serial.Serial.flushInput
        self.arduino.flushInput()
        self.arduino.setDTR(True)
        sleep(2)

        self.travel_speed = 25
        self.move_speed = 50

        self.last_position = (100, 100)
        self.cmd_queue = Queue()

    def init_motors(self):
        self.write("HOME\n")

    def wait_for_status(self):
        while self.arduino.read() == b'':
            pass
        response = self.arduino.readline().decode('utf-8').rstrip()
        print(f"Response from Arduino: {response}")
        sleep(.05)

    def write_queue(self):
        msg = ""
        while not self.cmd_queue.empty():
            if msg != "":
                msg += "|"
            msg += self.cmd_queue.get()
        msg += "\n"
        self.write(msg)

    def write(self, command):
        self.arduino.write(command.encode('utf-8'))
        self.wait_for_status()

    def move_axes(self, pos_x, pos_y):
        # We are going to assume that this is NOT an active move, so we are going to go as fast as we can
        speed = 25
        pos_x *= 100
        pos_y *= 100
        command = f"MV {pos_y} {pos_x} {speed} {speed}"
        self.last_position = (pos_x, pos_y)
        self.cmd_queue.put(command)

    def synchronized_move(self, pos_x, pos_y, time):
        # I don't care about time, just that the motors travel in a straight line to their destination
        pos_x *= 100
        pos_y *= 100
        dx = abs(pos_x - self.last_position[0])
        dy = abs(pos_y - self.last_position[1])

        theta = np.arctan(dy/dx)
        delay_x = round(self.move_speed * np.cos(theta))
        delay_y = round(self.move_speed * np.sin(theta))

        command = f"MV {pos_y} {pos_x} {delay_y} {delay_x}"
        self.last_position = (pos_x, pos_y)
        self.cmd_queue.put(command)

    def kill(self):
        pass


class DualAxis:

    def __init__(self):
        self.base_queue = Queue()
        self.center_queue = Queue()
        self.base_status = Queue()
        self.center_status = Queue()
        self.base_lock = threading.Lock()
        self.center_lock = threading.Lock()
        self.threads = []
        self.base_steps = 0
        self.center_steps = 0

        self.base_axis = ThreadedAxis(1, "Base-Axis", 1, self.base_queue, self.base_status, (16, 20, 13, 5, 25),
                                      self.base_lock, self.center_lock)
        self.center_axis = ThreadedAxis(2, "Center-Axis", 2, self.center_queue, self.center_status,
                                        (12, 19, 26, 24, 23), self.center_lock, self.base_lock)

        self.base_axis.start()
        self.center_axis.start()

        self.threads.append(self.base_axis)
        self.threads.append(self.center_axis)

        self.wait_for_status("BOTH")

    def wait_for_status(self, axis):
        if axis == "BASE" or axis == "BOTH":
            while self.base_status.qsize() < 2:
                sleep(.1)
            base_type = self.base_status.get()
            if base_type == 0:
                self.base_steps = self.base_status.get()
            else:
                self.base_status.get()
        if axis == "CENTER" or axis == "BOTH":
            while self.center_status.qsize() < 2:
                sleep(.1)
            center_type = self.center_status.get()
            if center_type == 0:
                self.center_steps = self.center_status.get()
            else:
                self.center_status.get()

    def wait_for_threads(self):
        for t in self.threads:
            t.join()

    def move_axes(self, pos_1, pos_2):
        self.base_queue.put(1)
        self.base_queue.put(pos_1)
        self.center_queue.put(1)
        self.center_queue.put(pos_2)

        self.wait_for_status("BOTH")

    def synchronized_move(self, pos_1, pos_2, time):
        self.base_queue.put(2)
        self.center_queue.put(2)
        self.base_queue.put(pos_1)
        self.center_queue.put(pos_2)
        self.base_queue.put(time)
        self.center_queue.put(time)

        self.wait_for_status("BOTH")

    def kill(self):
        self.base_queue.put(0)
        self.center_queue.put(0)


