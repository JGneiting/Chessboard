from JoyconInterface.Joycon import StandardChessJoycon
from GameFiles.GameInterface import GameInterface
from NeopixelLights.LightInterface import LightsInterface
from BoardFiles import set_5v
import time


if __name__ == "__main__":
    set_5v(True)
    game_interface = GameInterface()
    light_interface = LightsInterface()
    joycon_r = StandardChessJoycon("RIGHT", game_interface, light_interface)
    joycon_l = StandardChessJoycon("LEFT", game_interface, light_interface)
    while True:
        # print(joycon_r.get_status())
        # print(joycon_l.get_status())
        time.sleep(.1)
