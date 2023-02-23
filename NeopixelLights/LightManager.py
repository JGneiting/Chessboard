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
            start = self.ending_square - (pps * square_num)
            end = start + 2
        else:
            end = pps * square_num + self.starting_square + 3 - adj
            start = end - 2

        end = math.floor(end)
        start = math.floor(start)
        return start, end


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
    starting_square = 83
    ending_square = 103


class SegmentLower(Segment):
    root = 114
    starting_square = 121
    ending_square = 141


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


class BoardLights:
    num_pixels = 152
    base_color = (58, 6, 61)
    select_color = (255, 255, 0)

    def __init__(self):
        self.lights = neopixel.NeoPixel(board.D12, self.num_pixels, auto_write=False)
        self.segments = []  # type: list[Segment]
        self.corners = []  # type: list[PlayerSide]
        self.stop = False

        self.segments.append(SegmentLeft(38, False))
        self.segments.append(SegmentUpper(38, False))
        self.segments.append(SegmentRight(38, True))
        self.segments.append(SegmentLower(38, True))

        self.corners.append(WhiteSideLights(self.lights, (0, 0, 255), self.base_color))
        self.corners.append(BlackSideLights(self.lights, (255, 0, 0), self.base_color))

        self.lights.fill(self.base_color)
        self.flush()

    def light_ranges(self, ranges, color):
        for start, end in ranges:
            self.light_range((start, end), color)

    def highlight_square(self, square, color=(255, 255, 255)):
        self.lights.fill(self.base_color)

        ranges = self.get_pixel_locations(square)
        self.light_ranges(ranges, color)

        self.flush()

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
        source_range = self.get_pixel_locations(source)
        dest_range = self.get_pixel_locations(dest)
        for i in range(4):
            self.light_ranges(source_range, (0, 255, 0))
            self.light_ranges(dest_range, (255, 0, 0))
            self.flush()
            time.sleep(0.5)
            self.light_ranges(source_range, self.base_color)
            self.light_ranges(dest_range, self.base_color)
            self.flush()
            time.sleep(0.5)

    def light_range(self, pos, color):
        for i in range(pos[0], pos[1]):
            self.lights[i] = color

    def run_pregame(self):
        # TODO: Create a pregame show of lights for the homing process
        pass
