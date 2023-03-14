from GameFiles.StateManager import ChessLogic
import threading
from GameFiles.ChessErrors import *
import time


class Player:

    def __init__(self, game_interface):
        self.board = game_interface  # type: GameInterface
        self.color = game_interface.add_player(self)
        self.inverted = self.color == "Black"
        self.upgrading = False
        self.selection = None
        self.active = True
        print(self.color)

    def set_active(self, active):
        self.active = active

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
        # self.board.move_piece(source, dest)
        self.board.move = (source, dest)

    def upgrade_pawn(self, pawn):
        """
        This function needs overridden by the player interface to select a target piece type
        :param pawn: Pawn object being upgraded
        :return:
        """
        return "Queen"

    def submit_upgrade(self, piece_type):
        self.selection = piece_type

    def cleanup(self):
        pass


class GameInterface(ChessLogic):
    team_order = ["White", "Black"]
    movement_time = 1.5
    assigned = 0
    move = None

    def __init__(self, error_queue=None, capture_callback=None, castle_callback=None, upgrade_callback=None):
        super().__init__()

        self.players = []
        self.error_report = error_queue
        self.capture_call = capture_callback
        self.castle_call = castle_callback
        self.upgrade_call = upgrade_callback
        self.active = True

    def set_active(self, active):
        self.active = active
        for player in self.players:
            player.set_active(active)

    def get_active_player(self):
        index = self.team_order.index(self.turn)
        return self.players[index]

    def capture(self, piece, square):
        self.capture_call(piece)
        super().capture(piece, square)

    def castle(self, king, rook, destination):
        rook_source = rook.get_location()
        rook_loc = super().castle(king, rook, destination)
        self.castle_call(rook_loc, rook_source)

    def get_pawn_upgrade(self, pawn):
        self.get_active_player().upgrade_pawn(pawn)
        self.upgrade_call(pawn, self.get_active_player())

    def cleanup(self):
        for player in self.players:
            player.cleanup()

    def add_player(self, interface):
        if self.assigned < 2:
            self.players.append(interface)
            self.assigned += 1
            return self.team_order[self.assigned - 1]
        else:
            raise PlayerError

    def signal_player(self):
        for player in self.players:
            if player.color == self.turn:
                print(f"It is {self.turn}'s turn")
                player.my_turn()

    def next_player(self):
        super().next_player()
        # self.signal_player()

    def move_piece(self, source, dest):
        try:
            super().move_piece(source, dest)
            # self.move = (source, dest)
            return
        except Checkmate as e:
            if self.error_report:
                self.error_report.put(e)
            self.turn = None
            self.move = (source, dest)
        except TurnError as e:
            if self.error_report:
                self.error_report.put(e)
        except InvalidMove as e:
            if self.error_report:
                self.error_report.put(e)

    def get_move(self):
        while self.move is None:
            time.sleep(.1)
            if not self.error_report.empty():
                break
        self.move_piece(*self.move)
        temp = self.move
        self.move = None
        return temp

    def wait_for_upgrade(self, pawn, player):
        while player.upgrading:
            time.sleep(1)
        selection = player.selection
        super().upgrade_pawn(pawn, selection)
        return selection
