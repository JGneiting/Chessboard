import os
import random
from SoundPlayer.ManagerExtensions import SoundChannel, BackgroundChannel


class StandardChessBackground(BackgroundChannel):
    song_lib = ""
    thread_id = 6
    assigned_channel = 0

    def __init__(self, sound_interface):
        super().__init__(sound_interface, self.assigned_channel)
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

    def pause(self):
        self.current_message.add_argument("Pause", True)
        self.play_sound()

    def unpause(self):
        self.current_message.add_argument("Pause", False)
        self.play_sound()

    def stop(self):
        self.set_fade(500)
        self.stop_playback()


class IntroMusic(StandardChessBackground):
    assigned_channel = 0
    song_lib = "SoundPlayer/GameSounds/Intro"


class MidrollMusic(StandardChessBackground):
    assigned_channel = 1
    song_lib = "SoundPlayer/GameSounds/Midroll"


class OutroMusic(StandardChessBackground):
    assigned_channel = 2
    song_lib = "SoundPlayer/GameSounds/Outro"


class CheckMusic(StandardChessBackground):
    assigned_channel = 3
    song_lib = "SoundPlayer/GameSounds/Game Event Tracks/Check"
    return_track = None


class ChessSFX(SoundChannel):

    def __init__(self, sound_interface):
        super().__init__(sound_interface, 1)


