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
        self.fullmoves = 0
        self.halfmoves = 0
        self.moves = []

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

    def get_last_move(self):
        if len(self.moves) > 0:
            return self.moves[-1]
        return "LOL"

    def checked(self, team):
        return self.in_check == team

    def get_valid_moves(self, square):
        if not self.square_empty(square):
            return self.get_square(square).get_possible_moves()
        return []

    def reset_board(self):
        self.board = [[None] * 8 for i in range(8)]
        self.initialize_board()

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
        back = ["Rook", "Knight", "Bishop", "Queen", "King", "Bishop", "Knight", "Rook"]
        for color in ["White", "Black"]:
            row = 0 if color == "White" else 7
            for i in range(8):
                self.board[row][i] = eval(f'{back[i]}(self.numeric_to_named(row, i), self.numeric_to_named(row, i), color, self)')
        for color in ["White", "Black"]:
            row = 1 if color == "White" else 6
            for i in range(8):
                self.board[row][i] = eval(f'Pawn(self.numeric_to_named(row, i), self.numeric_to_named(row, i), color, self)')


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

    def create_simulator(self):
        return Simulator(self)

    def simulate_move(self, piece, square):
        test_board = self.create_simulator()
        test_board.move_piece(piece.get_location(), square)
        return not test_board.checked(piece.get_team())

    def generate_fen_string(self):
        board_fen = ""
        black_king = None
        white_king = None
        # Generate the piece placement. black is lowercase and white is uppercase
        reverse_order_rows = []
        for row, i in zip(self.board, range(len(self.board))):
            row_fen = ""
            empty = 0
            for square in row:
                if square is None or type(square) == GhostPawn:
                    empty += 1
                else:
                    if empty != 0:
                        row_fen += str(empty)
                        empty = 0
                    character = str(square)
                    if character == "King":
                        if square.get_team() == "White":
                            white_king = square
                        else:
                            black_king = square
                    if character == "Knight":
                        character = "N"
                    character = character[0]
                    if square.get_team() == "Black":
                        character = character.lower()
                    row_fen += character
            if empty != 0:
                row_fen += str(empty)
            reverse_order_rows.append(row_fen)

        reverse_order_rows.reverse()
        for fen in reverse_order_rows:
            board_fen += f"{fen}/"
        board_fen = board_fen[:-1]
        board_fen += " "

        # Add a character to indicate whose turn it is
        if self.turn == "White":
            board_fen += "w "
        else:
            board_fen += "b "

        # We need to check if either king can castle
        white_king.get_possible_moves()
        black_king.get_possible_moves()
        castle_fen = ""
        if white_king.castling_side[0]:
            castle_fen += "Q"
        if white_king.castling_side[1]:
            castle_fen += "K"
        if black_king.castling_side[0]:
            castle_fen += "q"
        if black_king.castling_side[1]:
            castle_fen += "k"
        if castle_fen == "":
            castle_fen = "-"
        board_fen += f"{castle_fen} "

        # We need to identify any en passant squares
        if len(self.ghosts) != 0:
            ghost_fen = ""
            for ghost in self.ghosts:
                square = ghost.get_location().lower()
                ghost_fen += square
            board_fen += f"{ghost_fen} "
        else:
            board_fen += "- "

        # We need to add the number of halfmoves and fullmoves
        board_fen += f"{self.halfmoves} {self.fullmoves}"

        return board_fen

    def castle(self, king, rook, destination):
        # Determine what side the king is coming from
        alpha_key = king.character_swap(destination[0])
        if king.get_location()[0] < rook.get_location()[0]:
            # The king is on the left of the rook
            rook_loc = f"{king.character_swap(alpha_key-1)}{destination[1]}"
        else:
            # The king is on the right of the rook
            rook_loc = f"{king.character_swap(alpha_key+1)}{destination[1]}"
        self.set_square(rook_loc, rook)
        self.set_square(rook.get_location(), None)
        rook.set_location(rook_loc)
        return rook_loc

    def upgrade_pawn(self, pawn, target_piece_name):
        new_piece = eval(f"{target_piece_name}(0, pawn.get_location(), pawn.get_team(), self)")
        wrapped_pawn = SuperPawn(new_piece)
        self.set_square(pawn.get_location(), wrapped_pawn)

    def get_pawn_upgrade(self, pawn):
        """
        This function provides an access point to upgrade pawns from
        MUST BE OVERRIDDEN
        :return:
        """
        raise PawnUpgrade

    def move_piece(self, source, dest):
        success = False
        occupant = self.get_square(source)
        if occupant is not None:
            if occupant.get_team() != self.turn and type(self) != Simulator:
                raise TurnError(self.turn)
            move_set = occupant.get_possible_moves()
            if move_set is not None and dest in move_set:
                self.halfmoves += 1
                capture = self.get_square(dest)
                if str(capture) == "GhostPawn" and str(occupant) == "Pawn":
                    capture = capture.get_linked_pawn()
                    self.set_square(capture.get_location(), None)
                for ghost in self.ghosts:
                    self.set_square(ghost.get_location(), None)
                    del ghost
                self.ghosts = []
                if capture is not None and str(capture) != "GhostPawn":
                    capture.kill()
                    self.capture(capture, dest)
                if str(occupant) == "Pawn":
                    self.halfmoves = 0
                    occupant.remove_double()
                    if abs(int(occupant.get_location()[1]) - int(dest[1])) == 2:
                        passed_square = f"{dest[0]}{int((int(occupant.get_location()[1]) + int(dest[1]))/2)}"
                        ghost = GhostPawn(occupant, passed_square, occupant.get_team(), self)
                        self.set_square(passed_square, ghost)
                        self.ghosts.append(ghost)
                elif str(occupant) == "King":
                    if abs(self.named_to_numeric(dest)[1] - self.named_to_numeric(source)[1]) == 2:
                        # This is a castling move, we need to find the target rook
                        if self.named_to_numeric(dest)[1] > self.named_to_numeric(source)[1]:
                            row = "H"
                        else:
                            row = "A"
                        rook = self.get_square(f"{row}{source[1]}")
                        self.castle(occupant, rook, dest)
                occupant.set_location(dest)
                self.set_square(source, None)
                self.set_square(dest, occupant)
                self.in_check = None
                occupant.moved = True
                success = True
                self.moves.append(f"{source}{dest}".lower())
                self.run_check_cycle()
                if str(occupant) == "Pawn" and type(self) != Simulator:
                    try:
                        occupant.check_upgrade()
                    except PawnUpgrade as e:
                        self.get_pawn_upgrade(occupant)
                if occupant.get_team() == "Black":
                    self.fullmoves += 1
                self.next_player()
                self.run_stalemate_test()
            else:
                raise InvalidMove(dest, move_set)
        return success

    def run_stalemate_test(self):
        if len(self.get_team_moves(self.turn, True)) == 0 or self.halfmoves >= 100:
            raise Stalemate()

    def capture(self, piece, square):
        self.halfmoves = 0
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

    def get_team_moves(self, team, ignore_team=False):
        team_moves = {}
        temp = self.turn
        if ignore_team:
            self.turn = team
        for i in range(8):
            for j in range(8):
                if self.board[i][j] is not None and self.board[i][j].get_team() == team:
                    piece = self.board[i][j]
                    moves = piece.get_possible_moves()
                    if moves:
                        team_moves[piece.get_location()] = moves
        self.turn = temp
        return team_moves

    def get_team_pieces(self, team):
        pieces = []
        for i in range(8):
            for j in range(8):
                if self.board[i][j] is not None and (self.board[i][j].get_team() == team or team == "ALL"):
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

    def run_stalemate_test(self):
        pass