from BoardFiles import Board, magnet_push, magnet_pull


class BoardLogic(Board):

    def __init__(self):
        super().__init__(magnet_pull, magnet_push)
