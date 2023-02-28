import threading
import queue
from NeopixelLights.LightManager import BoardLights


class ThreadedLights(threading.Thread):

    def __init__(self, thread_id, name, counter, command_queue):
        super().__init__()
        self.threadID = thread_id
        self.name = name
        self.counter = counter
        self.queue = command_queue  # type: queue.Queue

        self.lights = BoardLights()

    def run(self):
        status = 0
        while status != -1:
            command = self.queue.get(block=True)
            if command == "Pregame":
                self.lights.run_pregame()
            elif command == "Select":
                square = self.queue.get(block=True)
                slot = self.queue.get(block=True)
                self.lights.highlight_square(square, slot)
            elif command == "Turn":
                team = self.queue.get(block=True)
                self.lights.indicate_player(team)
            elif command == "Move":
                source = self.queue.get(block=True)
                dest = self.queue.get(block=True)
                self.lights.indicate_move(source, dest)


class LightsInterface:

    def __init__(self):
        self.commands = queue.Queue()
        self.command_thread = ThreadedLights(3, "Lights", 3, self.commands)

        self.command_thread.start()

    def __del__(self):
        self.commands.put(-1)
        self.command_thread.join()

    def run_pregame(self):
        self.commands.put("Pregame")

    def select_square(self, square, slot):
        self.commands.put("Select")
        self.commands.put(square)
        self.commands.put(slot)

    def set_team(self, team):
        self.commands.put("Turn")
        self.commands.put(team)

    def indicate_move(self, source, dest):
        self.commands.put("Move")
        self.commands.put(source)
        self.commands.put(dest)
