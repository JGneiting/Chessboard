from GameFiles.StateManager import ChessLogic
from GameFiles.ChessErrors import PlayerError


class Player:

    def __init__(self, game_interface):
        self.board = game_interface  # type: GameInterface
        self.color = game_interface.add_player(self)

    def my_turn(self):
        pass

    def query_my_turn(self):
        return self.color == self.board.get_turn()

    def query_moves(self):
        return self.board.get_team_moves(self.color)

    def query_square(self, square):
        return self.board.get_square(square)

    def query_pieces(self):
        return self.board.get_team_pieces(self.color)

    def make_move(self, source, dest):
        self.board.move_piece(source, dest)

    def upgrade_pawn(self, pawn):
        # TODO: This function will need to be overridden to handle querying a piece type from the user
        return None

    def __del__(self):
        pass


class GameInterface(ChessLogic):
    team_order = ["White", "Black"]
    assigned = 0

    def __init__(self):
        super().__init__()

        self.players = []

    def add_player(self, interface):
        if self.assigned < 2:
            self.players.append(interface)
            self.assigned += 1
            return self.team_order[self.assigned]
        else:
            raise PlayerError

    def next_player(self):
        super().next_player()
        for player in self.players:
            if player.color == self.turn:
                player.my_turn()
