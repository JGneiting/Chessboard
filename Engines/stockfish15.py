from CPUChessPlayers.UCIPlayer import UCIPlayer

def create(backend, color):
    return UCIPlayer(backend, "/home/pi/Stockfish-sf_15/src", "stockfish", color)

