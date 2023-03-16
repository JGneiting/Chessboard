import math

from pyjoycon import get_L_id, get_R_id, ButtonEventJoyCon
from GameFiles.GameInterface import Player
from NeopixelLights.LightInterface import LightsInterface
from JoyconInterface.RumbleJoycon import RumbleJoyCon, RumbleData
import numpy as np
import threading
import queue
import time


class StickMonitor(threading.Thread):
    tolerance = 350
    bouncetime = .25

    def __init__(self, thread_id, name, counter, stick_type, callback, joycon, comm_queue):
        super().__init__()
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.event_callback = callback
        self.joycon = joycon  # type: ButtonEventJoyCon
        self.message = comm_queue  # type: queue.Queue
        self.stick_type = stick_type

    def get_stick(self):
        if self.stick_type == "LEFT":
            return self.joycon.get_stick_left_vertical(), self.joycon.get_stick_left_horizontal()
        else:
            return self.joycon.get_stick_right_vertical(), self.joycon.get_stick_right_horizontal()

    def get_home(self):
        home = [0, 0]
        for i in range(10):
            x, y = self.get_stick()
            home[0] += x
            home[1] += y
            time.sleep(.25)
        return home[0] / 10, home[1] / 10

    def run(self):
        home = self.get_home()
        run = True
        while run:
            current = self.get_stick()
            if abs(current[0] - home[0]) > self.tolerance or abs(current[1] - home[1]) > self.tolerance:
                self.event_callback()
                time.sleep(self.bouncetime)
            time.sleep(.1)
            if not self.message.empty():
                message = self.message.get()
                if message == 0:
                    run = False
                elif message == "Recalibrate":
                    time.sleep(.5)
                    home = self.get_home()

        print("Stick Monitor Exiting")


class StandardChessJoycon(ButtonEventJoyCon, RumbleJoyCon, Player):
    controller_count = 1
    rumble_type = RumbleData(400, 800, .8)

    def __init__(self, side, game_interface, light_interface=None, sfx_track=None):
        if side == "LEFT":
            id_ = get_L_id()
            self.delta = -1
        else:
            id_ = get_R_id()
            self.delta = 1
        ButtonEventJoyCon.__init__(self, *id_, track_sticks=True)
        Player.__init__(self, game_interface)
        self.enable_vibration()
        self.set_player_lamp(self.controller_count)
        self.controller_count += 1

        self.lights = light_interface  # type: LightsInterface
        self.side = side
        self.sfx = sfx_track
        self.state_function = self.piece_selection
        self.monitor_comm = queue.Queue()
        self.stick_monitor = StickMonitor(4, "Monitor", 4, side, self.stick_event, self, self.monitor_comm)
        self.stick_monitor.start()

        self.cursor = self.query_pieces()[0].get_location()
        self.stick_home = self.get_home()

        self.selected = None
        self.upgrade_order = ["Queen", "Bishop", "Knight", "Rook"]
        if self.color == "White":
            self.select_first()

    def upgrade_pawn(self, pawn):
        self.upgrading = True
        self.cursor = 0
        self.state_function = self.select_upgrade_type
        if self.sfx:
            self.sfx.set_song("Instructions")
            self.sfx.play_sound()

    def cleanup(self):
        self.monitor_comm.put(0)
        self.stick_monitor.join()

    def get_home(self):
        home = [0, 0]
        for i in range(10):
            x, y = self.get_raw_stick()
            home[0] += x
            home[1] += y
            time.sleep(.25)
        return home[0] / 10, home[1] / 10

    def my_turn(self):
        self.select_first()

    def get_raw_stick(self):
        if self.side == "LEFT":
            return self.get_stick_left_vertical(), self.get_stick_left_horizontal()
        else:
            return self.get_stick_right_vertical(), self.get_stick_right_horizontal()

    def get_stick(self):
        if self.side == "LEFT":
            return self.get_stick_left_vertical() - self.stick_home[1], \
                   self.get_stick_left_horizontal() - self.stick_home[0]
        else:
            return self.get_stick_right_vertical() - self.stick_home[1], \
                   self.get_stick_right_horizontal() - self.stick_home[0]

    def draw_cursor(self):
        if self.lights:
            # print(f"Drawing Cursor: {self.cursor}")
            if self.state_function == self.piece_selection:
                self.lights.select_square(self.cursor, 0)
            elif self.state_function == self.move_selection:
                self.lights.select_square(self.cursor, 1)

    def select_first(self):
        pieces = self.query_pieces()
        self.cursor = pieces[0].location
        self.lights.select_square(self.cursor, 0)

    def translate_square(self, square):
        translation = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8}
        x = translation[square[0]]
        y = int(square[1])
        return x, y

    def translate_point(self, point):
        translation = {1:'A', 2:'B', 3:'C', 4:'D', 5:'E', 6:'F', 7:'G', 8:'H'}
        square = f'{translation[point[0]]}{point[1]}'
        return square

    def create_map(self, squares):
        coords = []
        for square in squares:
            x, y = self.translate_square(square)
            coords.append((x, y))
        return coords

    def get_vector(self, theta):
        return np.cos(theta), np.sin(theta)

    def select_in_direction(self, direction, plot):
        angle_deltas = []
        distances = []
        source = self.translate_square(self.cursor)
        direction = (direction * np.pi) / 180
        for point in plot:
            dx = point[0] - source[0]
            dy = point[1] - source[1]
            dist = math.sqrt(dx**2 + dy**2)
            distances.append(dist)
            vec_1 = (dx, dy)
            vec_2 = self.get_vector(direction)
            angle_deltas.append(self.angle_between_vectors(vec_1, vec_2))
        if len(distances) != 0:
            fitness = []
            for distance, angle in zip(distances, angle_deltas):
                score = (angle / 4) + distance
                fitness.append(score)

            # threshold = max(distances)**2
            min_fitness = 0
            for i in range(1, len(fitness)):
                if fitness[i] < fitness[min_fitness]:
                    min_fitness = i

            # if fitness[min_fitness] < threshold:
            self.cursor = self.translate_point(plot[min_fitness])

    def select_upgrade_type(self, button, state):
        if button == "Joystick":
            if state < 90 or state > 270:
                self.cursor += 1
                self.cursor %= len(self.upgrade_order)
            else:
                self.cursor -= 1
                if self.cursor < 0:
                    self.cursor += len(self.upgrade_order)
            if self.sfx:
                self.sfx.set_song(self.upgrade_order[self.cursor])
                self.sfx.play_sound()
        elif (button == 'x' or button == 'down') and state:
            self.submit_upgrade(self.upgrade_order[self.cursor])
            self.upgrading = False
            self.state_function = self.piece_selection

    def move_selection(self, button, state):
        if self.query_my_turn():
            if button == "Joystick":
                moves = self.selected.get_possible_moves()
                try:
                    moves.remove(self.cursor)
                except ValueError:
                    pass
                source_map = self.create_map(moves)
                self.select_in_direction(state, source_map)
                self.draw_cursor()
            if (button == 'x' or button == 'down') and state:
                if self.lights:
                    self.lights.indicate_move(self.selected.get_location(), self.cursor)
                self.make_move(self.selected.get_location(), self.cursor)
                self.state_function = self.piece_selection
            if (button == 'a' or button == 'left') and state:
                self.cursor = self.selected.get_location()
                self.state_function = self.piece_selection
                self.draw_cursor()

    def piece_selection(self, button, state):
        if self.query_my_turn():
            if button == "Joystick":
                pieces = self.query_pieces()
                squares = [piece.get_location() for piece in pieces]
                try:
                    squares.remove(self.cursor)
                except ValueError:
                    pass
                source_map = self.create_map(squares)
                self.select_in_direction(state, source_map)
                self.draw_cursor()
            if (button == 'x' or button == 'down') and state:
                try:
                    self.selected = self.query_square(self.cursor)
                    self.cursor = self.selected.get_possible_moves()[0]
                    self.state_function = self.move_selection
                    self.draw_cursor()
                except IndexError:
                    self._send_rumble(self.rumble_type.GetData())

    def recalibrate(self):
        self.stick_home = self.get_home()

    def joycon_button_event(self, button, state):
        # print(f"{button}: {state}")
        if self.board is not None and self.active:
            if self.query_my_turn() or self.upgrading:
                if (button == "zl" or button == "zr") and state:
                    self.recalibrate()
                else:
                    self.state_function(button, state)

    def stick_event(self):
        # print("Event")
        x, y = self.get_stick()
        if (self.inverted and self.side == "RIGHT") or (not self.inverted and self.side == "LEFT"):
            x *= -1
            y *= -1
        try:
            theta = self.angle_between_vectors((x, y), (1, 0))
            if y > 0:
                theta *= -1
                theta += 360
            if self.active:
                self.state_function("Joystick", theta)
        except ValueError:
            pass

    def angle_between_vectors(self, vec_1, vec_2):
        theta = np.arccos((np.dot((vec_1[0], vec_1[1]), (vec_2[0], vec_2[1])) /
                           (np.sqrt(np.dot((vec_1[0], vec_1[1]), (vec_1[0], vec_1[1]))))) *
                          np.sqrt(np.dot((vec_2[0], vec_2[1]), (vec_2[0], vec_2[1]))))
        theta /= np.pi
        theta *= 180
        theta = round(theta)
        return theta
