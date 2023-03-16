from GameFiles.GameInterface import Player
import subprocess
import time


class UCIPlayer(Player):

    def __init__(self, game_interface, uci_executable):
        super().__init__(game_interface)
        self.ponder_move = None
        self.think_time = 3
        self.player = subprocess.Popen(uci_executable)
        self.send("uci")
        self.wait_for_ready()

        self.send("ucinewgame")
        self.wait_for_ready()

        self.update_board_position()

    def update_board_position(self):
        fen = self.board.generate_fen_string()
        self.send(f"position fen {fen}")

    def my_turn(self):
        # If the last move made was the move being pondered, send ponderhit
        last_move = self.board.get_last_move()
        if last_move == self.ponder_move:
            self.send("ponderhit")
            time.sleep(self.think_time/2)
        else:
            self.update_board_position()
            self.send("go")
            time.sleep(self.think_time)
        output, error = self.send("stop")
        tokens = output.split(' ')
        move = tokens[1]
        source = move[:2].upper()
        dest = move[2:].upper()
        self.make_move(source, dest)

    def send(self, message):
        output, error = self.player.communicate(input=message)
        return output.decode("utf-8"), error.decode("utf-8")

    def wait_for_ready(self):
        output = None
        while output != "readyok":
            output, error = self.send("isready")
