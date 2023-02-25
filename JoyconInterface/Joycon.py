from pyjoycon import get_L_id, get_R_id, ButtonEventJoyCon
from GameFiles.GameInterface import Player
from NeopixelLights.LightInterface import LightsInterface
import numpy as np
import threading
import queue
import time


class StickMonitor(threading.Thread):
    tolerance = 100
    bouncetime = .5

    def __init__(self, thread_id, name, counter, stick_type, callback, joycon, quit_queue):
        super().__init__()
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.event_callback = callback
        self.joycon = joycon  # type: ButtonEventJoyCon
        self.quit = quit_queue  # type: queue.Queue
        self.stick_type = stick_type

    def get_stick(self):
        if self.stick_type == "LEFT":
            return self.joycon.get_stick_left_vertical(), self.joycon.get_stick_left_horizontal()
        else:
            return self.joycon.get_stick_right_vertical(), self.joycon.get_stick_right_horizontal()

    def run(self):
        home = self.get_stick()
        while self.quit.empty():
            current = self.get_stick()
            if abs(current[0] - home[0]) > self.tolerance or abs(current[1] - home[1]) > self.tolerance:
                self.event_callback()
                time.sleep(self.bouncetime)
            time.sleep(.1)


class StandardChessJoycon(ButtonEventJoyCon, Player):
    controller_count = 1

    def __init__(self, side, game_interface, light_interface=None):
        if side == "LEFT":
            id_ = get_L_id()
            self.delta = -1
        else:
            id_ = get_R_id()
            self.delta = 1
        ButtonEventJoyCon.__init__(self, *id_, track_sticks=True)
        Player.__init__(self, game_interface)
        self.set_player_lamp(self.controller_count)
        self.controller_count += 1

        self.lights = light_interface  # type: LightsInterface
        self.side = side
        self.state_function = self.piece_selection
        self.stick_halt = queue.Queue()
        self.stick_monitor = StickMonitor(4, "Monitor", 4, side, self.stick_event, self, self.stick_halt)
        self.stick_monitor.start()

        self.cursor = None
        self.stick_home = (0, 0)
        self.stick_home = self.get_stick()

    def __del__(self):
        self.stick_halt.put(0)
        self.stick_halt.join()
        ButtonEventJoyCon.__del__(self)
        Player.__del__(self)

    def my_turn(self):
        self.select_first()

    def get_stick(self):
        if self.side == "LEFT":
            return self.get_stick_left_vertical() - self.stick_home[1], \
                   self.get_stick_left_horizontal() - self.stick_home[0]
        else:
            return self.get_stick_right_vertical() - self.stick_home[1], \
                   self.get_stick_right_horizontal() - self.stick_home[0]

    def draw_cursor(self):
        if self.lights:
            if self.state_function == self.piece_selection:
                # TODO: LightsInterface needs multi-cursor support
                self.lights.select_square(self.cursor)
            else:
                self.lights.select_square(self.cursor)

    def select_first(self):
        pieces = self.query_pieces()
        self.cursor = pieces[0].location
        self.draw_cursor()

    def select_in_direction(self, direction):
        # TODO: Need to select the next valid square in the indicated direction
        pass

    def piece_selection(self, button, state):
        if button == "":
            pass

    def joycon_button_event(self, button, state):
        print(button)
        print(self.board)
        if self.board is not None:
            if self.query_my_turn():
                self.state_function(button, state)

    def stick_event(self):
        x, y = self.get_stick()
        theta = np.arccos((np.dot((x, y), (1, 0)) / np.sqrt(np.dot((x, y), (x, y)))))
        theta /= np.pi
        theta *= 180
        if y > 0:
            theta *= -1
            theta += 360
        theta = round(theta)
        if theta <= 22.5 or theta > 337.5:
            stick_dir = (1, 0)
        elif theta <= 67.5:
            stick_dir = (1, 1)
        elif theta <= 112.5:
            stick_dir = (0, 1)
        elif theta <= 157.5:
            stick_dir = (-1, 1)
        elif theta <= 202.5:
            stick_dir = (-1, 0)
        elif theta <= 247.5:
            stick_dir = (-1, -1)
        elif theta <= 292.5:
            stick_dir = (0, -1)
        elif theta <= 337.5:
            stick_dir = (1, -1)
        self.select_in_direction(stick_dir)
