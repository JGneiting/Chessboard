from flask import Flask
from WebConfig.DataStructures import PlayerConfig
import os
import pydbus
import bluetooth


import time
os.system("sudo invoke-rc.d bluetooth restart")

bus = pydbus.SystemBus()

adapter = bus.get('org.bluez', '/org/bluez/hci0')
mngr = bus.get('org.bluez', '/')

def list_connected_devices():
    mngd_objs = mngr.GetManagedObjects()
    for path in mngd_objs:
        con_state = mngd_objs[path].get('org.bluez.Device1', {}).get('Connected', False)
        addr = mngd_objs[path].get('org.bluez.Device1', {}).get('Address')
        name = mngd_objs[path].get('org.bluez.Device1', {}).get('Name')
        print(f"Device {name} found")


def remove_bad_joycons():
    mngd_objs = mngr.GetManagedObjects()
    for path in mngd_objs:
        con_state = mngd_objs[path].get('org.bluez.Device1', {}).get('Connected', False)
        addr = mngd_objs[path].get('org.bluez.Device1', {}).get('Address')
        name = mngd_objs[path].get('org.bluez.Device1', {}).get('Name')
        print(f"Device {name} found")
        if con_state:
            if not con_state and (name == "Joy-Con (R)" or name == "Joy-Con (L)"):
                print(f'Device {name} [{addr}] is not connected')
                adapter.RemoveDevice(path)

def joycon_search():
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    print("Found {} devices.".format(len(nearby_devices)))

    for addr, name in nearby_devices:
        print("  {} - {}".format(addr, name))


list_connected_devices()
remove_bad_joycons()
joycon_search()

app = Flask(__name__)
autoplay = False
running = False
new_game = False
game = None  # type: ChessGame
white = PlayerConfig()
black = PlayerConfig()

import time
from GameSupervisor.ChessGame import ChessGame
from WebConfig.routes import *


def launch_game():
    global running, game, new_game
    if running:
        game.set_player("White", white)
        game.set_player("Black", black)
        if not game.busy:
            new_game = True
            game.reset_game(force=True)
    else:
        game = ChessGame(white, black, launch_game)
        running = True
        new_game = True

def main():
    global new_game
    app.run()
    while True:
        while game is None and (not new_game or autoplay):
            time.sleep(.5)
        if autoplay:
            time.sleep(20)
        new_game = False
        game.run_game()



