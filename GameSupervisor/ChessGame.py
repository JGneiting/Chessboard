import os
import importlib.util
import sys

from NeopixelLights import LightsInterface
from GameSupervisor.BoardMovementLogic import BoardLogic
from GameSupervisor.SoundController import SoundController
from GameSupervisor.SupervisorErrors import *
from JoyconInterface.Joycon import StandardChessJoycon
from CPUChessPlayers.DemonstrationBots import *
from CPUChessPlayers.UCIPlayer import *
from GameFiles.GameInterface import GameInterface
from GameFiles.ChessErrors import *
from BoardFiles import cleanup, red_button
from queue import Queue
import RPi.GPIO as GPIO
import time


class ChessGame:

    def __init__(self, white, black, play_callback):
        GPIO.add_event_detect(red_button, GPIO.FALLING, self.button_press, 400)
        self.button_callback = self.reset_game
        self.upgrade = []
        self.castle_move = []
        self.backends = {}
        self.moves_since_check = 10
        self.errors = Queue()
        self.lights = LightsInterface()
        self.audio = SoundController()
        self.lights.run_pregame()
        self.audio.run_intro()
        self.board = BoardLogic()
        self.play_callback = play_callback
        self.busy = False
        self.joycon_players = [None, None]  # type: list[StandardChessJoycon]

        time.sleep(2)

        self.joycon_audio = self.audio.create_ryan()
        self.backends["Main"] = self.create_game_interface()

        self.set_player("White", white)
        self.set_player("Black", black)

        # self.joycon_l = StandardChessJoycon("LEFT", self.backends["Joycon"], self.lights, joycon_audio)

        # UCIPlayer(self.backends["Joycon"], "/home/pi/Stockfish-sf_15/src", "stockfish")
        # UCIPlayer(self.backends["Joycon"], "/home/pi/lc0/build/release", "lc0", args=["--weights=/home/pi/Documents/Maia Nets/maia-1100.pb", "--backend=blas"])
        # self.joycon_r = StandardChessJoycon("RIGHT", self.backends["Joycon"], self.lights, joycon_audio)
        # UCIPlayer(self.backends["Joycon"], "/home/pi/lc0/build/release", "lc0", args=["--weights=/home/pi/Documents/Maia Nets/maia-1100.pb", "--backend=blas"])

        # UCIPlayer(self.backends["Joycon"], "/home/pi/Stockfish-sf_15/src", "stockfish")
        # UCIPlayer(self.backends["Joycon"], "/home/pi/komodo-14/Linux", "komodo-14.1-linux")

        self.backends["Demo"] = self.create_game_interface()
        WhiteDemo(self.backends["Demo"], "white")
        BlackDemo(self.backends["Demo"], "black")
        self.backends["Demo"].set_active(False)

        self.backend = self.backends["Main"]

        time.sleep(2)

        # self.run_game()

    def set_player(self, color, config):
        if color == "White":
            index = 0
        else:
            index = 1

        if config.human:
            if self.joycon_players[index] is None:
                self.joycon_players[index] = StandardChessJoycon(config.engine, self.backends["Main"], self.lights, self.joycon_audio, color)
            else:
                self.backends["Main"].players[index] = self.joycon_players[index]
                self.joycon_players[index].color = color
                self.joycon_players[index].inverted = color == "Black"
        else:
            # engine = importlib.import_module(f"{config.engine}.py")
            spec = importlib.util.spec_from_file_location("engine", f"{config.engine}")
            module = importlib.util.module_from_spec(spec)
            sys.modules["engine"] = module
            spec.loader.exec_module(module)
            module.create(self.backends["Main"], color)

    def switch_backend(self, backend_name):
        previous = None
        for name, backend in self.backends.items():
            if backend.active:
                previous = backend
            if name == backend_name:
                self.backend = backend
                backend.set_active(True)
            else:
                backend.set_active(False)
        previous.error_report.put(BackendSwitch)

    def toggle_demo(self):
        if self.backends["Demo"].active:
            self.switch_backend("Main")
        else:
            self.switch_backend("Demo")

    def create_game_interface(self):
        return GameInterface(self.errors, self.capture, self.castle, self.upgrade_pawn)

    def button_press(self, state):
        print("BUTTON PRESSED")
        if self.button_callback:
            self.button_callback()

    def reset_game(self, force=False):
        # Must hold button for 2 seconds to reset board
        time.sleep(2)
        if not GPIO.input(red_button) or force:
            self.audio.signal_mode_switch()
            # Holding it 2 more will switch the backend
            switch = False
            time.sleep(2)
            if not GPIO.input(red_button):
                self.audio.signal_mode_switch()
                switch = True
            # self.button_callback = None
            self.audio.stop_midroll()
            self.play_again(switch)

    def capture(self, piece):
        self.board.capture(piece)

    def castle(self, source, dest):
        print("Castling")
        self.castle_move = [source, dest]

    def upgrade_pawn(self, pawn, player):
        self.audio.pause_midroll()
        target = self.backend.wait_for_upgrade(pawn, player)
        target_file = f'{target} Confirm'
        self.joycon_audio.set_song(target_file)
        self.audio.unpause_midroll()
        # TODO: Check if the target piece can be revived from the dead

    def play_again(self, switch=False):
        self.lights.stop_show()
        self.board.reset()
        self.audio.run_intro()
        self.lights.run_pregame()
        remaining_pieces = self.backend.get_team_pieces("ALL")
        # We need to move living pieces back to their starting square
        for piece in remaining_pieces:
            self.board.move_home(piece)
        self.board.return_captured()
        self.backend.reset_board()
        if switch:
            self.toggle_demo()

    def joycon_reset(self):
        for joycon, i in zip(self.joycon_players, range(2)):
            if joycon is not None:
                side = joycon.side
                color = joycon.color
                ping = joycon == self.backend.get_active_player()

                del joycon
                self.joycon_players[i] = StandardChessJoycon(side, self.backend, self.lights, self.joycon_audio, color)

                if ping:
                    self.joycon_players[i].my_turn()

    def quit(self):
        self.backend.cleanup()
        self.lights.cleanup()
        self.board.cleanup()
        self.audio.cleanup()

        cleanup()

    def run_game(self):
        self.backend.turn = "White"
        self.lights.stop_show()
        self.lights.set_team("White")
        self.audio.run_midroll()
        self.button_callback = self.reset_game
        run = True
        self.busy = True
        while run:
            try:
                self.backend.signal_player()
                source, dest = self.backend.get_move()
                if not self.errors.empty():
                    raise self.errors.get()
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
            except BackendSwitch:
                pass
            except Checkmate as e:
                piece = str(self.backend.get_square(dest))
                if piece is "None":
                    piece = "Knight"
                print(f"{piece} ============================")
                if piece == "Knight":
                    print("Knight detected")
                    self.board.move_between(source, dest, 1)
                else:
                    self.board.move_piece(source, dest, 1)
                print(e)
                self.audio.run_outro()
                self.lights.run_postgame(e.winner)
                self.button_callback = self.play_callback
                run = False
                # GPIO.remove_event_detect(red_button)
                # channel = GPIO.wait_for_edge(red_button, GPIO.FALLING, timeout=150000)
                # if channel is None:
                #     run = False
                #     print("Exiting")
                # else:
                #     time.sleep(2)
                #     switch = False
                #     if not GPIO.input(red_button):
                #         self.audio.signal_mode_switch()
                #         switch = True
                #     # self.play_again()
                #     GPIO.remove_event_detect(red_button)
                #     GPIO.add_event_detect(red_button, GPIO.FALLING, self.button_press, 400)
            except Stalemate as e:
                print(e)
                self.audio.run_stalemate()
                self.lights.run_postgame(None)
                self.button_callback = self.play_callback
                run = False
                # GPIO.remove_event_detect(red_button)
                # channel = GPIO.wait_for_edge(red_button, GPIO.FALLING, timeout=150000)
                # if channel is None:
                #     run = False
                #     print("Exiting")
                # else:
                #     time.sleep(2)
                #     switch = False
                #     if not GPIO.input(red_button):
                #         self.audio.signal_mode_switch()
                #         switch = True
                #     # self.play_again(switch)
                #     GPIO.remove_event_detect(red_button)
                #     GPIO.add_event_detect(red_button, GPIO.FALLING, self.button_press, 400)

        # time.sleep(20)
        # self.reset_game(force=True)
        self.busy = False
