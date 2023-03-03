import os
import random
from SoundPlayer.ManagerExtensions import SoundChannel, BackgroundChannel


class StandardChessBackground(BackgroundChannel):
    song_lib = ""
    thread_id = 6

    def __init__(self, sound_interface):
        super().__init__(sound_interface, 0)
        self.thread_id += 1

        self.song_list = os.listdir(self.song_lib)
        random.shuffle(self.song_list)
        self.next_song = 0

    def play_next(self):
        self.set_song_by_file(f"{self.song_lib}/{self.song_list[self.next_song]}")
        self.set_fade(500)
        self.play_sound()

        self.next_song += 1
        self.next_song %= len(self.song_list)


class IntroMusic(StandardChessBackground):
    song_lib = "SoundPlayer/GameSounds/Intro"


class MidrollMusic(StandardChessBackground):
    song_lib = "SoundPlayer/GameSounds/Midroll"


class OutroMusic(StandardChessBackground):
    song_lib = "SoundPlayer/GameSounds/Outro"


class ChessSFX(SoundChannel):

    def __init__(self, sound_interface):
        super().__init__(sound_interface, 1)


