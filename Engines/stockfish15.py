from CPUChessPlayers.UCIPlayer import UCIPlayer

def create(backend):
    return UCIPlayer(backend, "/home/pi/Stockfish-sf_15/src", "stockfish")

