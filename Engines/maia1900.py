from CPUChessPlayers.UCIPlayer import UCIPlayer

def create(backend, color):
    return UCIPlayer(backend, "/home/pi/lc0/build/release", "lc0", color, args=["--weights=/home/pi/Documents/Maia Nets/maia-1900.pb", "--backend=blas"])

