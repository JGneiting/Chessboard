from BoardFiles.MotorManager import DualAxis
from BoardFiles.MagnetManager import Magnet
from time import sleep


class Board:
    inverted = False

    def __init__(self, magnet_pull, magnet_push):
        self.magnet = Magnet(magnet_pull, magnet_push)
        self.axis = DualAxis()
        self.location = [1, 1]

        self.sq_1 = (.88, .86)
        self.sq_2 = (.134, .855)
        self.sq_3 = (.133, .13)
        self.sq_4 = (.89, .147)
        self.overshoot = .0025
        self.rail_compensate = .0015

    def active_move(self, square, time):
        self.magnet.activate()
        self.move_to_square(square, time, compensate=True)
        self.move_to_square(square, .25)
        sleep(.5)
        self.magnet.deactivate()
        for i in range(10):
            self.magnet.activate()
            sleep(.05)
            self.magnet.deactivate()
            sleep(.05)

    def invert(self):
        self.inverted = True

    def move_piece(self, source, destination, time):
        self.move_to_square(source, time)
        self.active_move(destination, time)

    def move_to_square(self, square, time, compensate=False):
        """
        Moves carriage to named square
        :param square: String based on chess naming conventions
        :param time: Time to take on the move
        :param compensate: Overshoot destination to account for piece friction
        :param invert: Bool to invert the board
        :return:
        """
        x_target, y_target = self.convert_square_to_absolute(square)

        if compensate:
            x_dir = x_target - self.location[0]
            y_dir = y_target - self.location[1]
            x_coeff = 0
            y_coeff = 0
            if x_dir < 0:
                x_coeff = -1
            if x_dir > 0:
                x_coeff = 1
            if y_dir < 0:
                y_coeff = -1
            if y_dir > 0:
                y_coeff = 1
            x_target += self.overshoot * x_coeff
            y_target += self.overshoot * y_coeff

        self.axis.synchronized_move(x_target, y_target, time)
        self.location = [x_target, y_target]

    def convert_square_to_absolute(self, square):
        row = square[0]
        col = int(square[1])
        alphas = ["A", "B", "C", "D", "E", "F", "G", "H"]
        i = 0
        while alphas[i] != row:
            i += 1
        i += 1

        if self.inverted:
            col = abs(col - 9)
            i = abs(i - 9)

        left_x_range = self.sq_2[0] - self.sq_3[0]
        left_x = (8 - i) / 7 * left_x_range + self.sq_3[0]

        right_x_range = self.sq_1[0] - self.sq_4[0]
        right_x = (8 - i) / 7 * right_x_range + self.sq_4[0]

        x_range = right_x - left_x
        x_target = (8 - col) / 7 * x_range + left_x

        lower_y_range = self.sq_4[1] - self.sq_3[1]
        lower_y = (8 - col) / 7 * lower_y_range + self.sq_3[1]

        upper_y_range = self.sq_1[1] - self.sq_2[1]
        upper_y = (8 - col) / 7 * upper_y_range + self.sq_2[1]

        y_range = upper_y - lower_y
        y_target = (8 - i) / 7 * y_range + lower_y

        return (x_target, y_target)

    def close(self):
        self.axis.kill()
        self.axis.wait_for_threads()
