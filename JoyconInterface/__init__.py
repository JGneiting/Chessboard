from JoyconInterface.Joycon import StandardChessJoycon
from GameFiles.GameInterface import GameInterface
import time


if __name__ == "__main__":
    game_interface = GameInterface()
    joycon_r = StandardChessJoycon("RIGHT", game_interface)
    # joycon_l = StandardChessJoycon(None, "LEFT")
    while True:
        # print(joycon_r.get_status())
        # print(joycon_l.get_status())
        time.sleep(.1)
