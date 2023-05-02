import time
from WebConfig.DataStructures import PlayerConfig
from GameSupervisor.ChessGame import ChessGame
from WebConfig.routes import *


def launch_game():
    global running, game, new_game
    if running:
        game.set_player("White", white)
        game.set_player("Black", black)
        if not game.busy:
            new_game = True
    else:
        game = ChessGame(white, black, launch_game)
        running = True
        new_game = True

def main():
    global new_game
    app = Flask(__name__)
    while True:
        while game is None and (not new_game or autoplay):
            time.sleep(.5)
        new_game = False
        game.run_game()


autoplay = False
running = False
new_game = False
game = None  # type: ChessGame
white = PlayerConfig()
black = PlayerConfig()
