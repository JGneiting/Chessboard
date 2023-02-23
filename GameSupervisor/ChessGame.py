from GameFiles import ChessLogic
from NeopixelLights import LightsInterface
from GameSupervisor.BoardMovementLogic import BoardLogic
from GameFiles.ChessErrors import *


class ChessGame:

    def __init__(self):
        self.backend = ChessLogic()
        self.lights = LightsInterface()
        self.lights.run_pregame()

        self.board = BoardLogic()

        self.lights.set_team("White")
        self.run_game()

    def run_game(self):
        run = True
        try:
            while run:
                try:
                    source = input("Source: ")
                    dest = input("Destination: ")
                    if self.backend.move_piece(source, dest):
                        # TODO: Knights need moved with the special function
                        self.lights.indicate_move(source, dest)
                        self.board.move_piece(source, dest, 1)
                        self.lights.set_team(self.backend.get_turn())
                except TurnError as e:
                    # TODO: Play light sequence to assert whose turn it is
                    print(e)
                except InvalidMove as e:
                    # TODO: Play light sequence to indicate that move is invalid
                    print(e)
        except Checkmate as e:
            print(e)
            run = False
