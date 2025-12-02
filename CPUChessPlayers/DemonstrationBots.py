from GameFiles.GameInterface import Player


class Demo(Player):
    move_list = []

    def __init__(self, interface, color):
        super().__init__(interface, color)
        self.current_move = 0

    def my_turn(self):
        source, dest = self.move_list[self.current_move]
        self.make_move(source, dest)
        self.current_move += 1
        self.current_move %= len(self.move_list)


class WhiteDemo(Demo):
    move_list = [("B1", "A3"),
                 ("A3", "B5"),
                 ("D2", "D4"),
                 ("C1", "H6"),
                 ("E2", "E4"),
                 ("D1", "E2"),
                 ("E1", "C1"),
                 ("C2", "D3"),
                 ("D4", "D5"),
                 ("B2", "B3"),
                 ("A2", "B3"),
                 ("D5", "C6"),
                 ("E2", "H5")]


class BlackDemo(Demo):
    move_list = [("B7", "B5"),
                 ("C8", "A6"),
                 ("H7", "H5"),
                 ("G7", "H6"),
                 ("F7", "F6"),
                 ("A6", "B5"),
                 ("B5", "D3"),
                 ("B8", "C6"),
                 ("C6", "A5"),
                 ("A5", "B3"),
                 ("C7", "C5"),
                 ("A8", "B8")]
