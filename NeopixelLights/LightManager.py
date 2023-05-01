from queue import Queue
import threading
import random
import board
import neopixel
import math
import time


class Segment:
    root = 0
    starting_square = 9
    ending_square = 29

    def __init__(self, num_pixels, inverted):
        self.size = num_pixels
        self.inverted = inverted

    def get_segment_location(self, square_num):
        pps = (self.ending_square - self.starting_square) / 8
        adj = (square_num+1) % 2
        if self.inverted:
            start = self.ending_square - (pps * square_num) - 1
            end = start + 2
        else:
            end = pps * square_num + self.starting_square + 3 - adj
            start = end - 2

        end = math.floor(end)
        start = math.floor(start)
        return start, end-1

    def get_range(self):
        return self.starting_square, self.ending_square


class SegmentLeft(Segment):
    root = 0
    starting_square = 9
    ending_square = 29


class SegmentUpper(Segment):
    root = 38
    starting_square = 47
    ending_square = 67


class SegmentRight(Segment):
    root = 76
    starting_square = 84
    ending_square = 104


class SegmentLower(Segment):
    root = 114
    starting_square = 122
    ending_square = 142


class BoardCorner:
    num_pixels = 152

    def __init__(self, color, start, end, num_pixels=152):
        self.color = color
        self.num_pixels = num_pixels

        self.corner_start = start
        self.corner_end = end


class PlayerSide:
    num_pixels = 152
    delay = 0.2
    corners = []

    def __init__(self, pixel_array, color, inactive_color=(0,0,0), num_pixels=152):
        self.pixels = pixel_array
        self.num_pixels = num_pixels
        self.color = color
        self.inactive = inactive_color

    def activate(self):
        for i in range(2):
            self.set_side(True)
            time.sleep(self.delay)
            self.set_side(False)
            time.sleep(self.delay)
        self.set_side(True)

    def set_side(self, active):
        for start, end in self.corners:
            for i in range(abs((end-start) % self.num_pixels)):
                if active:
                    self.pixels[(start + i) % self.num_pixels] = self.color
                else:
                    self.pixels[(start + i) % self.num_pixels] = self.inactive
        self.pixels.show()


class WhiteSideLights(PlayerSide):
    corners = [(143, 9), (105, 122)]


class BlackSideLights(PlayerSide):
    corners = [(29, 47), (67, 85)]


class ShowRunner(threading.Thread):
    num_lights = 152

    def __init__(self, commands, lights):
        super().__init__()
        self.threadID = 7
        self.name = "Show Runner"
        self.counter = 7
        self.command_queue = commands
        self.lights = lights
        self.step = 1
        self.winner = None

    def step_pregame(self):
        seed = self.step/7
        delta = self.step * 1.05
        lighted = 0
        for i in range(round(19 + delta), round(self.num_lights + 19 + delta)):
            pixel = i % self.num_lights

            if 0 < lighted < 38 or 76 < lighted < 114:
                r = 255*(lighted % 38 / 38)
                seed += 0.25
            else:
                r = 0
                seed -= 0.25
            g = (255 - r) * (math.cos((lighted % 76 + (math.pi / 3)) / 76) ** 4)
            b = (255 - r) * (math.sin((lighted % 76 + ((2 * math.pi) / 3)) / 76) ** 4)
            self.lights[pixel] = (r, g, b)
            lighted += 1

        self.step += 1
        self.lights.show()

    def step_postgame(self):
        # Black will run first half of lights
        # White will run second half
        if self.winner:
            seed = self.step / 7
            black_range = range(19, 95)
            lighted = 0
            for i in range(19, self.num_lights + 19):
                pixel = i % self.num_lights
                if (pixel in black_range and self.winner == "Black") or (self.winner == "White" and pixel not in black_range):
                    r = 255 * (math.sin(1.05 * seed / 2) ** 4)
                    g = 255 * (math.sin((seed + (math.pi / 3))) ** 4)
                    b = 255 * (math.sin((seed + ((2 * math.pi) / 3)) / 3) ** 4)
                    self.lights[pixel] = (r, g, b)
                    if lighted < len(black_range) / 2:
                        seed += 0.25
                    else:
                        seed -= 0.25
                    lighted += 1
            self.lights.show()
            self.step += 1

    def reset_lights(self):
        pass

    def run(self):
        command = 0
        while command != -1:
            if not self.command_queue.empty():
                command = self.command_queue.get()
            if command == "Pregame":
                self.step = 1
                command = "Pregame Run"
            elif command == "Pregame Run":
                self.step_pregame()
            elif command == "Postgame":
                self.step = 1
                self.lights.fill((255, 0, 0))
                self.lights.show()
                self.winner = self.command_queue.get(block=True)
                command = "Postgame Run"
            elif command == "Postgame Run":
                self.step_postgame()
            elif command == "Stop":
                self.reset_lights()
                command = 0
            time.sleep(0.01)


class BoardLights:
    num_pixels = 152
    base_color = (58, 6, 61)
    slot_colors = [(255, 255, 0), (0, 255, 0)]

    def __init__(self):
        self.lights = neopixel.NeoPixel(board.D21, self.num_pixels, auto_write=False)
        self.segments = []  # type: list[Segment]
        self.corners = []  # type: list[PlayerSide]
        self.slots = [None, None]
        self.stop = False
        self.show_commands = Queue()

        self.segments.append(SegmentLeft(38, False))
        self.segments.append(SegmentUpper(38, False))
        self.segments.append(SegmentRight(38, True))
        self.segments.append(SegmentLower(38, True))
        self.show = ShowRunner(self.show_commands, self.lights)

        self.corners.append(WhiteSideLights(self.lights, (255, 0, 0), self.base_color))
        self.corners.append(BlackSideLights(self.lights, (0, 0, 255), self.base_color))

        self.lights.fill(self.base_color)
        self.flush()
        self.show.start()

    def cleanup(self):
        self.show_commands.put(-1)
        self.show.join()

    def light_ranges(self, ranges, color):
        for start, end in ranges:
            self.light_range((start, end), color)

    def blend(self, color_1, color_2):
        hybrid = [0, 0, 0]

        for c1, c2, i in zip(color_1, color_2, range(2)):
            hybrid[i] = (c1 + c2) / 2

        return hybrid

    def highlight_square(self, square, slot=0):
        self.clear_segments()
        self.slots[slot:] = [None] * (len(self.slots) - slot)
        self.slots[slot] = square
        self.draw_slots()

    def draw_slots(self):
        ranges = []
        for square in self.slots:
            if square is not None:
                ranges.append(self.get_pixel_locations(square))

        unique = []
        color = []

        for i in range(len(ranges)):
            current_color = self.slot_colors[i]
            for pixel_range in ranges[i]:
                if pixel_range in unique:
                    index = unique.index(pixel_range)
                    color[index] = self.blend(color[index], current_color)
                else:
                    unique.append(pixel_range)
                    color.append(current_color)

        for i in range(len(unique)):
            self.light_range(unique[i], color[i])

        self.flush()

    def clear_segments(self):
        for segment in self.segments:
            self.light_range(segment.get_range(), self.base_color)

    def get_pixel_locations(self, square):
        char_map = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
        row = char_map[square[0]]
        col = int(square[1]) - 1
        ranges = [self.segments[0].get_segment_location(col), self.segments[2].get_segment_location(col),
                  self.segments[1].get_segment_location(row), self.segments[3].get_segment_location(row)]

        return ranges

    def flush(self):
        self.lights.show()

    def indicate_player(self, team):
        if team == "White":
            self.corners[0].activate()
            self.corners[1].set_side(False)
        else:
            self.corners[0].set_side(False)
            self.corners[1].activate()

    def indicate_move(self, source, dest):
        self.slots = [source, dest]
        for i in range(4):
            self.draw_slots()
            time.sleep(0.5)
            self.clear_segments()
            self.flush()
            time.sleep(0.5)

    def light_range(self, pos, color):
        for i in range(pos[0], pos[1]+1):
            self.lights[i] = color

    def run_pregame(self):
        self.show_commands.put("Pregame")

    def stop_show(self):
        self.show_commands.put("Stop")
        self.lights.fill(self.base_color)

    def run_postgame(self, team):
        self.show_commands.put("Postgame")
        self.show_commands.put(team)
