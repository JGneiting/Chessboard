from SoundPlayer.ChessSounds import *
from SoundPlayer.SoundManager import SoundInterface
import pygame


class SoundController:

    def __init__(self):
        pygame.mixer.init(buffer=4096)
        pygame.init()

        self.interface = SoundInterface()
        self.intro_track = IntroMusic(self.interface)
        self.midroll_track = MidrollMusic(self.interface)
        self.outro_track = OutroMusic(self.interface)


    def cleanup(self):
        self.interface.cleanup()

    def run_intro(self):
        self.intro_track.play_next()
        self.outro_track.stop()
        self.intro_track.subscribe()

    def run_midroll(self):
        self.midroll_track.play_next()
        self.intro_track.stop()
        self.midroll_track.subscribe()

    def run_outro(self):
        self.outro_track.play_next()
        self.midroll_track.stop()
        self.outro_track.subscribe()


