import copy

from GameFiles.ChessPieces import *
from GameFiles.ChessErrors import *


class InternalBoard:
    def __init__(self):
        self.board = [[None] * 8 for i in range(8)]  # type: list[list[Piece]]
        self.captured = []
        self.ghosts = []
        self.in_check = None
        self.turn = "White"

        self.initialize_board()

    def __str__(self):
        out = ""
        for row in self.board:
            for square in row:
                if square is None:
                    out += "-"
                else:
                    out += str(square)[0]
                out += " "
            out += "\n"

        return out

    def get_square(self, square):
        x, y = self.named_to_numeric(square)
        return self.board[x][y]

    def square_empty(self, square):
        return self.get_square(square) is None

    def get_turn(self):
        return self.turn

    def checked(self, team):
        return self.in_check == team

    def get_valid_moves(self, square):
        if not self.square_empty(square):
            return self.get_square(square).get_possible_moves()
        return []

    def get_opposing_team(self, team):
        if team == "White":
            return "Black"
        return "White"

    def set_square(self, square, value):
        x, y = self.named_to_numeric(square)
        self.board[x][y] = value

    def named_to_numeric(self, square):
        char_map = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7}
        if (int(square[1]) < 1 or int(square[1]) > 8) or square[0] not in char_map.keys():
            raise UnknownSquare(square)
        return int(square[1])-1, char_map[square[0]]

    def numeric_to_named(self, *args):
        char_map = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H"}
        return f'{char_map[args[1]]}{args[0]+1}'

    def initialize_board(self):
        captured = []
        back = ["Rook", "Knight", "Bishop", "King", "Queen", "Bishop", "Knight", "Rook"]
        for color in ["White", "Black"]:
            row = 0 if color == "White" else 7
            for i in range(8):
                self.board[row][i] = eval(f'{back[i]}((0,0), self.numeric_to_named(row, i), color, self)')
        for color in ["White", "Black"]:
            row = 1 if color == "White" else 6
            for i in range(8):
                self.board[row][i] = eval(f'Pawn((0,0), self.numeric_to_named(row, i), color, self)')


class ChessLogic(InternalBoard):
    def is_movable(self, piece, square):
        try:
            if not self.square_empty(square):
                occupant = self.get_square(square)
                if piece.get_team() == occupant.get_team():
                    return False
            if self.simulate_move(piece, square):
                return True
        except InvalidMove:
            return False

    def simulate_move(self, piece, square):
        test_board = Simulator(self)
        test_board.move_piece(piece.get_location(), square)
        return not test_board.checked(piece.get_team())

    def move_piece(self, source, dest):
        success = False
        occupant = self.get_square(source)
        if occupant is not None:
            if occupant.get_team() != self.turn:
                raise TurnError(self.turn)
            move_set = occupant.get_possible_moves()
            if move_set is not None and dest in move_set:
                capture = self.get_square(dest)
                if str(capture) == "GhostPawn":
                    capture = capture.get_linked_pawn()
                    self.set_square(capture.get_location(), None)
                for ghost in self.ghosts:
                    self.set_square(ghost.get_location(), None)
                    del ghost
                self.ghosts = []
                if capture is not None:
                    capture.kill()
                    self.capture(capture, dest)
                if str(occupant) == "Pawn":
                    occupant.remove_double()
                    if abs(int(occupant.get_location()[1]) - int(dest[1])) == 2:
                        passed_square = f"{dest[0]}{int((int(occupant.get_location()[1]) + int(dest[1]))/2)}"
                        ghost = GhostPawn(occupant, passed_square, occupant.get_team(), self)
                        self.set_square(passed_square, ghost)
                        self.ghosts.append(ghost)
                occupant.set_location(dest)
                self.set_square(source, None)
                self.set_square(dest, occupant)
                self.in_check = None
                success = True
                self.run_check_cycle()
                self.next_player()
            else:
                raise InvalidMove(dest, move_set)
        return success

    def capture(self, piece, square):
        self.captured.append(piece)

    def run_check_cycle(self):
        state = self.turn
        self.turn = self.get_opposing_team(self.turn)
        try:
            for q in range(2):
                for i in range(8):
                    for j in range(8):
                        if self.board[i][j] is not None:
                            if self.board[i][j].get_team() == self.turn:
                                moves = self.board[i][j].get_possible_moves()
                                for square in moves:
                                    occupant = self.get_square(square)
                                    if occupant and str(occupant) == "King" and occupant.get_team() != self.turn:
                                        raise Check
                self.turn = self.get_opposing_team(self.turn)
        except Check as e:
            self.in_check = self.get_opposing_team(self.turn)
            self.checkmate_test()
            self.turn = state
            return
        self.turn = state
        self.in_check = None

    def checkmate_test(self):
        temp = self.turn
        self.turn = self.get_opposing_team(self.turn)
        if len(self.get_team_moves(self.turn)) == 0:
            raise Checkmate(temp)
        self.turn = temp

    def get_team_moves(self, team):
        team_moves = {}
        for i in range(8):
            for j in range(8):
                if self.board[i][j] is not None and self.board[i][j].get_team() == team:
                    piece = self.board[i][j]
                    moves = piece.get_possible_moves()
                    if moves:
                        team_moves[piece.get_location()] = moves
        return team_moves

    def get_team_pieces(self, team):
        pieces = []
        for i in range(8):
            for j in range(8):
                if self.board[i][j] is not None and self.board[i][j].get_team() == team:
                    pieces.append(self.board[i][j])
        return pieces

    def next_player(self):
        self.turn = self.get_opposing_team(self.turn)


class Simulator(ChessLogic):
    def __init__(self, source):
        super().__init__()

        self.board = copy.deepcopy(source.board)
        self.turn = copy.deepcopy(source.turn)

        for i in range(8):
            for j in range(8):
                if self.board[i][j]:
                    piece = self.board[i][j]
                    piece.board = self

    def is_movable(self, piece, square):
        if not self.square_empty(square):
            occupant = self.get_square(square)
            if piece.get_team() == occupant.get_team():
                return False
        return True