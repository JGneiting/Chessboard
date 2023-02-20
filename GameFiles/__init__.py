from GameFiles.StateManager import ChessLogic


board = ChessLogic()


def move(source, dest):
    board.move_piece(source, dest)

def display():
    print(board)
