import board
import neopixel
import math


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


class BoardLights:
    num_pixels = 152

    def __init__(self):
        self.lights = neopixel.NeoPixel(board.D12, self.num_pixels)
        self.segments = []  # type: list[Segment]

        self.segments.append(SegmentLeft(38, False))
        self.segments.append(SegmentUpper(38, False))
        self.segments.append(SegmentRight(38, True))
        self.segments.append(SegmentLower(38, True))

    def highlight_square(self, square, color=(255, 255, 255)):
        char_map = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
        row = char_map[square[0]]
        col = int(square[1]) - 1

        self.light_range(self.segments[0].get_segment_location(col), color)
        self.light_range(self.segments[2].get_segment_location(col), color)
        self.light_range(self.segments[1].get_segment_location(row), color)
        self.light_range(self.segments[3].get_segment_location(row), color)

    def light_range(self, pos, color):
        for i in range(pos[0], pos[1]):
            self.lights[i] = color
