from NeopixelLights import LightsInterface
from GameSupervisor.BoardMovementLogic import BoardLogic
from GameSupervisor.SoundController import SoundController
from JoyconInterface.Joycon import StandardChessJoycon
from CPUChessPlayers.DemonstrationBots import *
from GameFiles.GameInterface import GameInterface
from GameFiles.ChessErrors import *
from BoardFiles import cleanup, red_button
from queue import Queue
import RPi.GPIO as GPIO
import time


class ChessGame:

    def __init__(self):
        GPIO.add_event_detect(red_button, GPIO.FALLING, self.button_press, 400)
        self.button_callback = None
        self.upgrade = []
        self.castle_move = []
        self.moves_since_check = 10
        self.errors = Queue()
        self.backend = GameInterface(self.errors, self.capture, self.castle, self.upgrade_pawn)
        self.lights = LightsInterface()
        self.audio = SoundController()
        self.lights.run_pregame()
        self.audio.run_intro()
        self.board = BoardLogic()

        time.sleep(2)

        joycon_audio = self.audio.create_ryan()
        # self.joycon_r = StandardChessJoycon("RIGHT", self.backend, self.lights, joycon_audio)
        # self.joycon_l = StandardChessJoycon("LEFT", self.backend, self.lights, joycon_audio)
        WhiteDemo(self.backend)
        BlackDemo(self.backend)

        time.sleep(2)
        self.audio.run_midroll()
        self.button_callback = self.reset_game
        self.lights.stop_show()
        self.lights.set_team("White")
        self.run_game()

    def button_press(self, state):
        if self.button_callback:
            self.button_callback()

    def reset_game(self):
        # Must hold button for 2 seconds to reset board
        time.sleep(2)
        if not GPIO.input(red_button):
            self.button_callback = None
            self.audio.stop_midroll()
            self.play_again()

    def capture(self, piece):
        self.board.capture(piece)

    def castle(self, source, dest):
        self.castle_move = [source, dest]

    def upgrade_pawn(self, pawn, player):
        self.audio.pause_midroll()
        target = self.backend.wait_for_upgrade(pawn, player)
        self.audio.unpause_midroll()
        # TODO: Check if the target piece can be revived from the dead

    def play_again(self):
        self.lights.stop_show()
        self.board.reset()
        self.audio.run_intro()
        self.lights.run_pregame()
        remaining_pieces = self.backend.get_team_pieces("ALL")
        # We need to move living pieces back to their starting square
        for piece in remaining_pieces:
            self.board.move_home(piece)
        self.backend.reset_board()
        self.board.return_captured()
        self.backend.turn = "White"
        self.lights.stop_show()
        self.lights.set_team("White")
        self.audio.run_midroll()
        self.button_callback = self.reset_game

    def run_game(self):
        run = True
        while run:
            try:
                self.backend.signal_player()
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
                if self.upgrade and False:
                    self.backend.wait_for_upgrade(self.upgrade[0], self.upgrade[1])
            except TurnError as e:
                # TODO: Play light sequence to assert whose turn it is
                print(e)
            except InvalidMove as e:
                # TODO: Play light sequence to indicate that move is invalid
                print(e)
            except Checkmate as e:
                print(e)
                self.audio.run_outro()
                self.lights.run_postgame(e.winner)
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
                self.lights.run_postgame(None)
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
