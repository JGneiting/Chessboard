import pygame
from pygame.mixer import Sound, Channel
import threading
from queue import Queue
from BoardFiles import set_5v


class SoundManager(threading.Thread):

    def __init__(self, thread_id, name, counter, command_queue, channels=3):
        super().__init__()
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.commands = command_queue  # type: Queue
        self.callback = None

        set_5v(True)
        self.currently_playing = False
        self.num_channels = channels
        pygame.mixer.set_num_channels(self.num_channels)

        self.channels = [Channel(i) for i in range(channels)]
        self.playing = [None] * channels  # type: list[Sound]

    def run(self):
        command = 0
        while command != -1:
            if not self.commands.empty():
                command = self.commands.get()
                if command == -1:
                    break
                if "Subscribe" in command.args.keys():
                    self.callback = command.args["Subscribe"]
                elif "Stop" in command.args.keys():
                    self.channels[command.args["Stop"]].fadeout(command.args["fade_ms"])
                else:
                    self.play_on_channel(**command.args)
            if not pygame.mixer.get_busy() and self.currently_playing:
                if self.callback:
                    self.callback()
                self.currently_playing = False
            pygame.time.delay(100)

    def set_channel_volume(self, channel=0, volume=1):
        self.channels[channel].set_volume(volume)

    def play_on_channel(self, channel=0, sound="", volume=1, loops=0, max_time=0, fade_ms=0):
        print(f"Playing sound {sound} on channel {channel}")
        selected_sound = Sound(sound)
        if self.channels[channel].get_busy():
            self.channels[channel].fadeout(500)
            # pygame.time.delay(500)
        self.channels[channel].play(selected_sound, loops, max_time, fade_ms)
        # selected_sound.play()
        self.set_channel_volume(channel, volume)
        self.currently_playing = True


class SoundInterface:

    def __init__(self):
        self.commands = Queue()
        self.player = SoundManager(5, "Sound Manager", 5, self.commands)
        self.player.start()

    def cleanup(self):
        self.commands.put(-1)
        self.player.join()

    def send_message(self, message):
        self.commands.put(message)
