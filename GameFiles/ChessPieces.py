from GameFiles.ChessErrors import *


class Piece:
    movement = [(0,1)]

    def __init__(self, a_loc, loc, team, board):
        self.abs_location = a_loc
        self.location = loc
        self.team = team
        self.board = board
        self.abs_location = (0, 0)
        self.dead = False

        if team != "Black" and team != "White":
            raise TeamError(team)

        if team == "Black":
            new_moveset = []
            for pair in self.movement:
                x, y = pair[0], pair[1]
                x *= -1
                y *= -1
                new_moveset.append((x, y))
            self.movement = new_moveset

    def kill(self):
        self.dead = True

    def __deepcopy__(self, memodict={}):
        return eval(f'{str(self)}(self.abs_location, self.location, self.team, None)')

    def get_team(self):
        return self.team

    def get_location(self):
        return self.location

    def set_location(self, square):
        self.location = square

    def character_swap(self, char):
        char_map = {1:"A", 2:"B", 3:"C", 4:"D", 5:"E", 6:"F", 7:"G", 8:"H"}
        if char in char_map.values():
            for key, value in char_map.items():
                if value == char:
                    return key
        else:
            try:
                return char_map[char]
            except KeyError:
                raise OutOfRange

    def get_possible_moves(self):
        if self.board.get_turn() != self.team:
            return []
        x, y = self.character_swap(self.location[0]), int(self.location[1])
        move_list = []
        for move in self.movement:
            try:
                x_new = x + move[0]
                y_new = y + move[1]
                x_new = self.character_swap(x_new)
                if y_new < 1 or y_new > 8:
                    raise OutOfRange
                if self.board.is_movable(self, f'{x_new}{y_new}'):
                    move_list.append(f'{x_new}{y_new}')
            except OutOfRange:
                pass

        return move_list

    def __str__(self):
        return f'{type(self)}'[30:-2]


class RangedPiece(Piece):
    def __init__(self, *args):
        super().__init__(*args)
        self.strains = []

        for pair in self.movement:
            strain = []
            dx, dy = pair[0], pair[1]
            for i in range(1, 9):
                strain.append((i * dx, i * dy))
            self.strains.append(strain)

    def get_possible_moves(self):
        if self.board.get_turn() != self.team:
            return []
        x, y = self.character_swap(self.location[0]), int(self.location[1])
        move_list = []
        for strain in self.strains:
            for move in strain:
                try:
                    # TODO: ranged pieces should not be blocked by GhostPawns
                    x_new = x + move[0]
                    y_new = y + move[1]
                    x_new = self.character_swap(x_new)
                    if y_new < 1 or y_new > 8:
                        raise OutOfRange
                    if self.board.is_movable(self, f'{x_new}{y_new}'):
                        move_list.append(f'{x_new}{y_new}')
                    if not self.board.square_empty(f'{x_new}{y_new}'):
                        break
                except OutOfRange:
                    pass
        return move_list


class Pawn(Piece):
    movement = [(0,1), (0,2), (-1,1), (1,1)]

    def __init__(self, *args):
        super().__init__(*args)
        self.moved = False

    def get_possible_moves(self):
        if self.board.get_turn() != self.team:
            return []
        squares = []
        if int(self.location[1]) == 1 or int(self.location[1]) == 8:
            raise PawnUpgrade
        x, y = self.character_swap(self.location[0]), int(self.location[1])
        y_new = y + self.movement[0][1]
        try:
            target = f'{self.character_swap(x)}{y_new}'
            if self.board.square_empty(target) and self.board.is_movable(self, target):
                squares.append(target)
                if not self.moved:
                    target = f'{self.character_swap(x)}{y_new + self.movement[0][1]}'
                    if self.board.square_empty(target) and self.board.is_movable(self, target):
                        squares.append(target)
        except OutOfRange:
            pass
        except UnknownSquare:
            pass

        for move in self.movement[2:]:
            try:
                occupant = self.board.get_square(f'{self.character_swap(move[0] + x)}{move[1] + y}')
                if occupant is not None and occupant.get_team() != self.team and self.board.is_movable(self, f'{self.character_swap(move[0] + x)}{move[1] + y}'):
                    squares.append(f'{self.character_swap(move[0] + x)}{move[1] + y}')
            except OutOfRange:
                pass
            except UnknownSquare:
                pass

        return squares

    def remove_double(self):
        if not self.moved:
            self.moved = True


class Knight(Piece):
    movement = [(1,2), (2,1), (-1,2), (2,-1), (1,-2), (-2,1), (-1,-2), (-2,-1)]


class Rook(RangedPiece):
    movement = [(1,0), (0,1), (-1,0), (0,-1)]


class Bishop(RangedPiece):
    movement = [(1,1), (-1,1), (-1,-1), (1,-1)]


class King(Piece):
    movement = [(1,0), (1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1)]


class Queen(RangedPiece):
    movement = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]


class GhostPawn(Pawn):

    def __init__(self, linked_pawn, location, team, board):
        super().__init__((0, 0), location, team, board)
        self.link = linked_pawn

    def __deepcopy__(self, memodict={}):
        return eval(f"GhostPawn(self.link, self.location, self.team, self.board)")

    def get_linked_pawn(self):
        return self.link
