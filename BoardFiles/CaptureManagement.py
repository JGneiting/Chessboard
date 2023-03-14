import math
import time


class SlotManager:
    extremes = (0.005, 0.995)
    slot_span = (0.078, 0.923)

    def __init__(self, board, magnet):
        self.board = board
        self.magnet = magnet

        self.slots = []
        self.generate_slots()

    def capture(self, piece):
        location = self.board.convert_square_to_absolute(piece.get_location())

        def fitness(capture_slot):
            entry = capture_slot.first
            distance = math.sqrt((location[0] - entry[0]) ** 2 + ((location[1] - entry[1]) ** 2))
            return distance
        # Determine what storage slot is closest to the piece
        sorted_slots = sorted(self.slots, key=fitness)  # type: list[CaptureSlot]

        for slot in sorted_slots:
            if slot.available(piece):
                slot.store_piece(piece)
                break

    def reset_board(self):
        # We want to pull pieces from the -Pawn slots first, then move the pawns onto the board
        def fitness(capture_slot):
            piece_type = capture_slot.piece_type
            score = 1 if piece_type == "-Pawn" else 2
            return score
        removal_order = sorted(self.slots, key=fitness)  # type: list[CaptureSlot]

        # Now call the remove function on each slot in the correct order
        for slot in removal_order:
            slot.remove()

    def generate_slots(self):
        # We are creating the vertical storage slots
        delta = self.slot_span[1] - 0.5
        delta /= 4
        # X is technically the vertical axes. They store any piece except for pawns
        for x, team in zip(self.extremes, ["Black", "White"]):
            for i in range(2):
                back = (x, self.slot_span[i])
                if i == 0:
                    front = (x, 0.5 - delta)
                    home_abs = self.board.convert_axes(0.5, 1)[1]
                else:
                    front = (x, 0.5 + delta)
                    home_abs = self.board.convert_axes(0.5, 0)[1]
                self.slots.append(CaptureSlot(back, front, home_abs, self.board, self.magnet, team=team, piece_type="Pawn"))

        # Y is on the player side and store the other team's pieces and only pawns
        for y in self.extremes:
            for i, team in zip(range(2), ["Black", "White"]):
                back = (self.slot_span[i], y)
                if i == 0:
                    front = (0.5 - delta, y)
                    home_abs = self.board.convert_axes(1, 0.5)[0]
                else:
                    front = (0.5 + delta, y)
                    home_abs = self.board.convert_axes(0, 0.5)[0]
                self.slots.append(CaptureSlot(back, front, home_abs, self.board, self.magnet, team=team, piece_type="-Pawn"))


class CaptureSlot:
    magnet_strength = 40

    def __init__(self, back, front, axis_abs, board, magnet, team=None, piece_type="ANY"):
        """
        Creates a capture slot to store captured pieces in
        :param back: Coordinate of first (deepest) slot
        :param front: Coordinate of last (shallowest) slot
        :param board: Reference to the Board within the Motor Management
        :param team: Team of pieces allowed to be stored in the slot
        :param piece_type: The type of piece allowed to be stored in the slot (Any, Pawn, -Pawn)
        """
        self.first = back
        self.last = front
        self.delta = (front[0] - back[0], front[1] - back[1])
        self.board = board
        self.magnet = magnet
        self.stored = []
        self.team = team
        self.piece_type = piece_type

        # ---- PREP ----
        # We need to know where our loading zone is
        load_x = self.first[0] + (self.delta[0] / 4)
        load_y = self.first[1] + (self.delta[1] / 4)
        self.central_axis = "X"

        # One of these values will not change. It needs to move half of the other's delta toward .5 .5
        offset = 0.05
        if load_x == self.first[0]:
            self.central_axis = "X"
            if load_x > 0.5:
                load_x -= abs(offset)
            else:
                load_x += abs(offset)
            load_y = axis_abs
        else:
            self.central_axis = "Y"
            if load_y > 0.5:
                load_y -= abs(offset)
            else:
                load_y += abs(offset)
            load_x = axis_abs

        self.loading_zone = (load_x, load_y)

    def available(self, piece):
        available = True
        # Check if the team can be in the slot
        if self.team is not None and piece.get_team() != self.team:
            available = False
        # Check if the piece type can be in the slot
        piece_name = piece.piece_type()
        if self.piece_type != "Any":
            if self.piece_type == "-Pawn":
                if piece_name == "Pawn":
                    available = False
            else:
                if piece_name != "Pawn":
                    available = False
        if len(self.stored) >= 4:
            available = False
        return available

    def remove(self):
        self.magnet.deactivate()
        while len(self.stored) > 0:
            piece = self.stored.pop()

            # ---- STAGE 1 ----
            # Move inactive magnet to the piece
            piece_loc = piece.abs_location
            self.board.axis.move_axes(*piece_loc)
            self.board.axis.write_queue()

            # ---- STAGE 2 ----
            # Move piece to the front loading slot
            self.board.axis.synchronized_move(self.last[0], self.last[1], 1)

            # ---- STAGE 3 ----
            # Move piece to the loading zone
            self.board.axis.synchronized_move(self.loading_zone[0], self.loading_zone[1], 1)

            # ---- STAGE 4 ----
            # This is where the algorithm will vary. If we store pawns, we do not care about letter positioning

            if self.piece_type == "Pawn":
                # ++++ PAWN STORAGE ++++
                # We need to move pawn to the center of the board
                self.board.move_absolute(0.5, 0.5)
                # Now we move it to its slot
                self.board.axis.synchronized_move(*self.board.convert_square_to_absolute(piece.home))
            else:
                # ++++ NON PAWN STORAGE ++++
                # We need to move the piece to its intermediate axis
                home = piece.home
                offset = 1
                if home[0] >= "E":
                    offset = -1
                neighbor = self.select_in_direction(offset, 0, home)
                home_coords = self.board.convert_square_to_absolute(home)
                neighbor_coords = self.board.convert_square_to_absolute(neighbor)
                intermediate = home_coords[1] + neighbor_coords[1]
                intermediate /= 2
                self.board.axis.synchronized_move(0.5, intermediate)

                # Move the pawn to be level with its square
                self.board.axis.synchronized_move(home_coords[0], intermediate)

                # Move into position
                self.board.move_to_square(home, 1, True, True)

            # ---- STAGE 5 ----
            # Congratulations! You have moved one piece out of the buffer and onto the board! Execute the masterpiece
            self.magnet.pulse(self.magnet_strength)
            self.board.axis.write_queue()
            self.magnet.deactivate()

    def store_piece(self, piece):
        """
        Stores a piece in the capture stack
        :param piece:
        :return:
        """
        index = len(self.stored)
        self.stored.append(piece)
        location = (self.first[0] + (self.delta[0]*index)/3, self.first[1] + (self.delta[1]*index)/3)
        piece.abs_location = location

        self.execute_path(piece, location)
        piece.dead = True

    def select_in_direction(self, x, y, source):
        char_map = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "H": 8}
        x0 = char_map[source[0]]
        y0 = int(source[1])
        y += y0
        x += x0
        name = f"{list(char_map.keys())[x-1]}{y}"
        return name

    def execute_path(self, piece, destination):
        """
        Calculates a path to store the piece
        :param piece: Piece to store
        :param destination: Slot to put it in
        :return:
        """
        # ---- PREP ----
        # Separate the loading_zone into x and y components
        load_x = self.loading_zone[0]
        load_y = self.loading_zone[1]

        # ---- STAGE 1 ----
        # We need to move an inactive magnet under the piece
        print(piece.get_location())
        self.board.move_to_square(piece.get_location(), 1)
        self.board.axis.write_queue()

        # ---- STAGE 2 ----
        # We need to move the piece to the first intermediate location
        loc = self.board.convert_square_to_absolute(piece.get_location())
        off_x = 1
        off_y = 1
        if loc[1] > 0.5:
            off_x *= -1
        if loc[0] > 0.5:
            off_y *= -1
        # We need to get the location of the square in that direction
        direction = self.select_in_direction(off_x, off_y, piece.get_location())
        direction = self.board.convert_square_to_absolute(direction)
        offset_1 = ((loc[0] + direction[0])/2, (loc[1] + direction[1])/2)
        self.board.axis.synchronized_move(offset_1[0], offset_1[1], 1)

        # ---- STAGE 3 ----
        # We need to move the piece to the correct central axis
        if self.central_axis == "X":
            # We need to keep offset 1 X value and replace the Y value
            offset_2 = (offset_1[0], load_y)
        else:
            # We need to keep offset 1 Y value and replace the X value
            offset_2 = (load_x, offset_1[1])
        self.board.axis.synchronized_move(offset_2[0], offset_2[1], 1)

        # ---- STAGE 4 ----
        # We need to stage the piece in the loading zone
        self.board.axis.synchronized_move(load_x, load_y, 1)

        # ---- STAGE 5 ----
        # We need to move the piece to the start of the stack
        self.board.axis.synchronized_move(self.last[0], self.last[1], 1)

        # ---- STAGE 6 ----
        # Move to the destination slot
        self.board.axis.synchronized_move(destination[0], destination[1], 1)

        # ---- STAGE 7 ----
        # We have successfully queued the path for the captured piece. Execute the masterpiece
        self.magnet.pulse(self.magnet_strength)
        # time.sleep(0.4)
        self.board.axis.write_queue()
        self.magnet.deactivate()
