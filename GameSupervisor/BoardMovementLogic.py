from BoardFiles import Board, magnet_push, magnet_pull, set_12v


class BoardLogic(Board):

    def __init__(self):
        set_12v(True)
        super().__init__(magnet_pull, magnet_push)
