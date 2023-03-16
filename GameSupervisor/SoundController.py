from SoundPlayer.ChessSounds import *
from SoundPlayer.SoundManager import SoundInterface
import time
import pygame


class SoundController:

    def __init__(self):
        pygame.mixer.init(buffer=4096, channels=10, size=-16)
        # pygame.init()

        self.interface = SoundInterface()
        self.intro_track = IntroMusic(self.interface)
        self.midroll_track = MidrollMusic(self.interface)
        self.outro_track = OutroMusic(self.interface)
        self.check_track = CheckMusic(self.interface)
        self.stalemate_track = StalemateMusic(self.interface)
        self.sfx = ChessSFX(self.interface)

    def create_ryan(self):
        return Ryan(self.interface)

    def cleanup(self):
        self.interface.cleanup()

    def run_intro(self):
        self.intro_track.play_next()
        self.outro_track.stop()
        self.intro_track.subscribe()

    def run_midroll(self):
        # self.midroll_track.play_next()
        self.midroll_track.subscribe()
        self.intro_track.stop()

    def stop_midroll(self):
        self.midroll_track.stop()

    def run_outro(self):
        self.outro_track.play_next()
        self.midroll_track.stop()
        self.check_track.stop()
        self.outro_track.subscribe()

    def play_check(self):
        self.midroll_track.stop()
        self.check_track.play_next()

    def run_stalemate(self):
        self.stalemate_track.play_next()
        self.midroll_track.stop()
        self.check_track.stop()
        self.stalemate_track.subscribe()

    def pause_midroll(self):
        self.midroll_track.pause()

    def unpause_midroll(self):
        self.midroll_track.unpause()

    def signal_mode_switch(self):
        self.sfx.set_song("Ready")
        self.sfx.play_sound()
