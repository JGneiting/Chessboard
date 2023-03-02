from NeopixelLights import LightsInterface
from GameSupervisor.BoardMovementLogic import BoardLogic
from GameSupervisor.SoundController import SoundController
from JoyconInterface.Joycon import StandardChessJoycon
from GameFiles.GameInterface import GameInterface
from GameFiles.ChessErrors import *
from BoardFiles import cleanup
from queue import Queue
import time


class ChessGame:

    def __init__(self):
        self.errors = Queue()
        self.backend = GameInterface(self.errors)
        self.lights = LightsInterface()
        self.audio = SoundController()
        self.lights.run_pregame()
        self.audio.run_intro()
        self.board = BoardLogic()

        self.joycon_r = StandardChessJoycon("RIGHT", self.backend, self.lights)
        self.joycon_l = StandardChessJoycon("LEFT", self.backend, self.lights)

        self.lights.set_team("White")
        self.audio.run_midroll()
        self.run_game()

    def run_game(self):
        run = False
        while run:
            try:
                source, dest = self.backend.get_move()
                print(f"{str(self.backend.get_square(dest))} ============================")
                if str(self.backend.get_square(dest)) == "Knight":
                    print("Knight detected")
                    self.board.move_between(source, dest, 1)
                else:
                    self.board.move_piece(source, dest, 1)
                self.lights.set_team(self.backend.get_turn())
                if not self.errors.empty():
                    raise self.errors.get()
            except TurnError as e:
                # TODO: Play light sequence to assert whose turn it is
                print(e)
            except InvalidMove as e:
                # TODO: Play light sequence to indicate that move is invalid
                print(e)
            except Checkmate as e:
                print(e)
                self.audio.run_outro()
                time.sleep(120)
                run = False

        self.backend.cleanup()
        self.lights.cleanup()
        self.board.cleanup()
        self.audio.cleanup()

        cleanup()
