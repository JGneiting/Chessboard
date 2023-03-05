from BoardFiles.MotorManager import DualAxis, SerialAxis
from BoardFiles.MagnetManager import Magnet
from BoardFiles.CaptureManagement import SlotManager
from time import sleep


class Board:
    inverted = True

    def __init__(self, magnet_pull, magnet_push):
        self.magnet = Magnet(magnet_pull, magnet_push)
        # self.axis = DualAxis()
        self.axis = SerialAxis()
        self.axis.init_motors()
        self.location = [1, 1]

        self.sq_1 = (.877, .86)
        self.sq_2 = (.128, .858)
        self.sq_3 = (.14, .14)
        self.sq_4 = (.89, .143)
        self.overshoot = .0025
        self.rail_compensate = .0015

        self.capture_manager = SlotManager(self, self.magnet)

    def cleanup(self):
        self.close()

    def capture(self, piece):
        self.capture_manager.capture(piece)

    def active_move(self, square, time):
        self.magnet.activate()
        self.move_to_square(square, time, compensate=True, active=True)
        # self.move_to_square(square, .25)
        self.axis.write_queue()
        sleep(.5)
        self.magnet.deactivate()
        for i in range(2):
            self.magnet.activate()
            sleep(.05)
            self.magnet.deactivate()
            sleep(.05)

    def invert(self):
        self.inverted = not self.inverted

    def move_piece(self, source, destination, time):
        self.move_to_square(source, time)
        self.axis.write_queue()
        self.active_move(destination, time)

    def move_between(self, source, dest, time):
        """
        This function requires that source and dest differ by only one in either letter or number
        :param source: Source square based on chess naming conventions
        :param dest: Destination square based on chess naming conventions
        :param time: Time to complete move
        :return:
        """
        start = self.convert_square_to_absolute(source)
        end = self.convert_square_to_absolute(dest)
        intermediates = []

        if abs(int(source[1]) - int(dest[1])) == 1:
            # Intermediate is halfway between in horizontal
            delta_x = (start[0] + end[0]) / 2
            delta_y1 = (((start[1] + end[1]) / 2) + start[1]) / 2
            delta_y2 = ((delta_y1 - start[1]) * 3) + start[1]
            intermediates.append((delta_x, delta_y1))
            intermediates.append((delta_x, delta_y2))
        else:
            # Intermediate is halfway between in vertical
            delta_x1 = (((start[0] + end[0]) / 2) + start[0]) / 2
            delta_x2 = ((delta_x1 - start[0]) * 3) + start[0]
            delta_y = (start[1] + end[1]) / 2
            intermediates.append((delta_x1, delta_y))
            intermediates.append((delta_x2, delta_y))
        self.move_to_square(source, time/4)
        self.axis.write_queue()
        self.magnet.pulse(60)
        self.axis.move_axes(intermediates[0][0], intermediates[0][1])
        self.axis.move_axes(intermediates[1][0], intermediates[1][1])
        self.location = (intermediates[1][0], intermediates[1][1])
        # self.magnet.set_duty_cycle(100)
        self.move_to_square(dest, time/4, active=True)
        self.axis.write_queue()
        self.magnet.deactivate()

    def move_to_square(self, square, time, compensate=False, active=False):
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

        if active:
            self.axis.synchronized_move(x_target, y_target, time)
        else:
            self.axis.move_axes(x_target, y_target)
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
        # self.axis.wait_for_threads()
