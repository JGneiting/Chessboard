import threading


class SoundManagerMessage:

    def __init__(self):
        self.args = {}

    def __str__(self):
        arg_str = ""
        for key, value in self.args.items():
            arg_str += f"{key}:{value} "
        return arg_str[0:-1]

    def add_argument(self, name, value):
        """
        Method will add arguments to the message
        :param name: Name of the argument to add (One of: channel sound volume loops max_time fade_ms
        :param value: The value to assign with the indicated argument
        :return:
        """
        self.args[name] = value


class SoundChannel:

    def __init__(self, sound_interface, channel_id, sound_list=None):
        if sound_list is None:
            sound_list = {}
        self.interface = sound_interface
        self.current_message = SoundManagerMessage()
        self.channel = channel_id
        self.sounds = sound_list

    def add_sound(self, name, file):
        self.sounds[name] = file

    def set_song_by_file(self, filename):
        self.current_message.add_argument("sound", filename)

    def set_song(self, name):
        self.current_message.add_argument("sound", self.sounds[name])

    def set_volume(self, volume):
        self.current_message.add_argument("volume", volume)

    def set_loops(self, loop_count):
        self.current_message.add_argument("loops", loop_count)

    def set_max_play_time(self, time):
        self.current_message.add_argument("max_time", time)

    def set_fade(self, ms):
        self.current_message.add_argument("fade_ms", ms)

    def play_sound(self):
        self.current_message.add_argument("channel", self.channel)
        self.interface.send_message(self.current_message)
        self.current_message = SoundManagerMessage()


class BackgroundChannel(SoundChannel):
    songs = []

    def __init__(self, sound_interface, channel_id):
        SoundChannel.__init__(self, sound_interface, channel_id)
        self.active = False

    def play_next(self):
        pass

    def subscribe(self):
        self.current_message.add_argument("Subscribe", self.play_next)
