import sys
import threading
from flask import Flask
from WebConfig.DataStructures import PlayerConfig
import os
import time
import subprocess
import pexpect
import re

def is_mac_address(mac_str):
    """Check if a string is a valid MAC address."""
    # Regular expression pattern for a MAC address
    pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
    return bool(re.match(pattern, mac_str))


os.system("sudo hciconfig hci0 reset")
os.system("sudo systemctl restart bluetooth")

time.sleep(2)

def remove_paired_joycons():
    # Start a bluetoothctl session
    session = pexpect.spawn("bluetoothctl")
    session.logfile = None

    # Wait for the bluetoothctl prompt
    session.expect(".*# ")

    # List all paired devices
    test = session.sendline("paired-devices")
    session.expect(".*# ")
    paired_devices_output = session.after.decode("utf-8")
    paired_devices = [line.split(" ")[1] for line in paired_devices_output.split("\n") if "Joy-Con" in line]

    # Remove all paired Joy-Con devices
    for device in paired_devices:
        session.sendline(f"remove {device}")
        session.expect(".*# ")

    # Exit the bluetoothctl session
    session.sendline("exit")
    session.expect(pexpect.EOF)


def connect_joycon():
    global right_connected, left_connected
    # Start a bluetoothctl session
    session = pexpect.spawn("bluetoothctl")
    session.logfile = None

    # Wait for the bluetoothctl prompt
    session.expect(".*# ")
    print("Connected to bluetoothctl.")

    # Scan for nearby devices
    session.sendline("scan on")
    session.expect_exact("Discovery started")
    session.expect(".*# ")
    print("Scanning for nearby devices...")
    session.sendline("devices")
    session.expect(".*# ")
    session.sendline("devices")

    # Find Joy-Con devices
    joycon_devices = []
    while True:
        # Check for new output from bluetoothctl
        try:
            output = session.read_nonblocking(1024, 10).decode("utf-8")
            print(f"Output received: {output}")
            if "Joy-Con" in output:
                for line in output.split("\n"):
                    if "Joy-Con" in line and not "[Joy-Con" in line:
                        fields = line.split(" ")

                        if len(fields) == 5:
                            mac_address = fields[2]
                            side = fields[4][1]
                            print(f"Found new Joy-Con: {mac_address}")
                        else:
                            mac_address = fields[1]
                            side = fields[3][1]
                            print(f"Found Joy-Con: {mac_address}")
                        joycon_devices.append((mac_address, side))
        except pexpect.TIMEOUT:
            pass

        # Stop scanning if no more devices are found
        if session.expect([".*# ", "Failed to start discovery", pexpect.TIMEOUT], timeout=5) != 0:
            break

    print("Scanning complete.")

    # Pair and connect to Joy-Con devices
    for joycon in joycon_devices:
        device = joycon[0]
        side = joycon[1]
        # Check if device is already paired
        session.sendline(f"info {device}")
        if is_mac_address(device) and session.expect(["Paired: yes", "Paired: no", pexpect.TIMEOUT]) == 1:
            # If not paired, pair the device
            session.sendline(f"pair {device}")
            if session.expect(["Pairing successful", "Passkey", "PIN code", pexpect.TIMEOUT]) == 1:
                session.sendline("0000")
                session.expect(["Pairing successful", "Failed to pair", pexpect.TIMEOUT])
            session.expect(".*# ")

        # Connect to device
        if is_mac_address(device):
            session.sendline(f"connect {device}")
            session.expect_exact("Connection successful")
            session.expect(".*# ")
            print(f"Connected to {device}.")
            if side == "R":
                right_connected = True
            else:
                left_connected = True

    # Exit the bluetoothctl session
    session.sendline("exit")
    session.expect(pexpect.EOF)
    print("Exited bluetoothctl.")


left_connected = False
right_connected = False

remove_paired_joycons()
# for i in range(3):
#     connect_joycon()
#     time.sleep(2.5)

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
    if not running:
        running = True
        game = ChessGame(white, black, launch_game)
    game.set_player("White", white)
    game.set_player("Black", black)
    if not game.busy:
        new_game = True
        # game.reset_game(force=True)


def assign_joycons():
    right_available = right_connected
    left_available = left_connected
    if white.human:
        if right_available:
            white.engine = "RIGHT"
            right_available = False
        elif left_available:
            white.engine = "LEFT"
            left_available = False
        else:
            return False
    if black.human:
        if right_available:
            black.engine = "RIGHT"
            right_available = False
        elif left_available:
            black.engine = "LEFT"
            left_available = False
        else:
            return False
    return True


def run_flask_app():
    app.run(host='0.0.0.0')


def main():
    global new_game
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
    while True:
        while not new_game or autoplay:
            time.sleep(.5)
        new_game = False
        if assign_joycons() and game is not None:
            game.run_game()
            time.sleep(20)
            game.reset_game(True)



