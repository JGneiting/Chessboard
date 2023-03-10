from NeopixelLights import LightsInterface
from GameSupervisor.BoardMovementLogic import BoardLogic
from GameSupervisor.SoundController import SoundController
from JoyconInterface.Joycon import StandardChessJoycon
from GameFiles.GameInterface import GameInterface
from GameFiles.ChessErrors import *
from BoardFiles import cleanup, red_button
from queue import Queue
import RPi.GPIO as GPIO
import time


class ChessGame:

    def __init__(self):
        GPIO.add_event_detect(red_button, GPIO.FALLING, self.button_press, 200)
        self.button_callback = None
        self.castle_move = []
        self.moves_since_check = 10
        self.errors = Queue()
        self.backend = GameInterface(self.errors, self.capture, self.castle)
        self.lights = LightsInterface()
        self.audio = SoundController()
        self.lights.run_pregame()
        self.audio.run_intro()
        self.board = BoardLogic()

        time.sleep(2)

        self.joycon_r = StandardChessJoycon("RIGHT", self.backend, self.lights)
        self.joycon_l = StandardChessJoycon("LEFT", self.backend, self.lights)

        self.audio.run_midroll()
        self.lights.set_team("White")
        self.run_game()

    def button_press(self):
        if self.button_callback:
            self.button_callback()

    def capture(self, piece):
        self.board.capture(piece)

    def castle(self, source, dest):
        self.castle_move = [source, dest]

    def play_again(self):
        self.board.reset()
        self.audio.run_intro()
        remaining_pieces = self.backend.get_team_pieces("ALL")
        # We need to move living pieces back to their starting square
        for piece in remaining_pieces:
            self.board.move_home(piece)
        self.backend.reset_board()
        self.board.return_captured()
        self.backend.turn = "White"
        self.lights.set_team("White")
        self.audio.run_midroll()

    def run_game(self):
        run = True
        while run:
            try:
                source, dest = self.backend.get_move()
                time.sleep(.1)
                piece = str(self.backend.get_square(dest))
                if piece is "None":
                    piece = "Knight"
                print(f"{piece} ============================")
                if piece == "Knight":
                    print("Knight detected")
                    self.board.move_between(source, dest, 1)
                else:
                    self.board.move_piece(source, dest, 1)
                self.lights.set_team(self.backend.get_turn())
                if self.backend.in_check is not None:
                    if self.moves_since_check is None or self.moves_since_check > 6:
                        self.audio.play_check()
                        self.moves_since_check = 0
                self.moves_since_check += 1
                if not self.errors.empty():
                    raise self.errors.get()
                if self.castle_move:
                    self.board.move_intermediate(*self.castle_move)
                    self.castle_move = []
            except TurnError as e:
                # TODO: Play light sequence to assert whose turn it is
                print(e)
            except InvalidMove as e:
                # TODO: Play light sequence to indicate that move is invalid
                print(e)
            except Checkmate as e:
                print(e)
                self.audio.run_outro()
                GPIO.remove_event_detect(red_button)
                channel = GPIO.wait_for_edge(red_button, GPIO.FALLING, timeout=150000)
                if channel is None:
                    run = False
                    print("Exiting")
                else:
                    self.play_again()
            except Stalemate as e:
                print(e)
                self.audio.run_stalemate()
                GPIO.remove_event_detect(red_button)
                channel = GPIO.wait_for_edge(red_button, GPIO.FALLING, timeout=150000)
                if channel is None:
                    run = False
                    print("Exiting")
                else:
                    self.play_again()

        self.backend.cleanup()
        self.lights.cleanup()
        self.board.cleanup()
        self.audio.cleanup()

        cleanup()
