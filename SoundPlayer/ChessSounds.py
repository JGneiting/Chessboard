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


class StalemateMusic(StandardChessBackground):
    assigned_channel = 2
    song_lib = "SoundPlayer/GameSounds/Game Event Tracks/Stalemate"


class ChessSFX(SoundChannel):
    channel = 4
    loc = "SoundPlayer/GameSounds/SFX"

    def __init__(self, sound_interface):
        super().__init__(sound_interface, self.channel)

        self.add_sound("Ready", f"{self.loc}/ReadyBeep.mp3")


class Ryan(SoundChannel):
    channel = 5
    loc = "SoundPlayer/GameSounds/SFX/Ryan"

    def __init__(self, sound_interface):
        super().__init__(sound_interface, self.channel)

        self.add_sound("Bishop", f"{self.loc}/Bishop Selection.mp3")
        self.add_sound("Knight", f"{self.loc}/Knight Selection.mp3")
        self.add_sound("Queen", f"{self.loc}/Queen Selection.mp3")
        self.add_sound("Rook", f"{self.loc}/Rook Selection.mp3")
        self.add_sound("Instructions", f"{self.loc}/Upgrade Instructions.mp3")
        self.add_sound("Bishop Confirm", f"{self.loc}/Bishop Selected.mp3")
        self.add_sound("Knight Confirm", f"{self.loc}/Knight Selected.mp3")
        self.add_sound("Queen Confirm", f"{self.loc}/Queen Selected.mp3")
        self.add_sound("Rood Confirm", f"{self.loc}/Rook Selected.mp3")
