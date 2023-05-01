from GameFiles.GameInterface import Player
import subprocess
import time


class UCIPlayer(Player):

    def __init__(self, game_interface, uci_path, uci_executable, args=[]):
        super().__init__(game_interface)
        self.ponder_move = None
        self.think_time = 3
        self.target_piece = "Queen"
        if args != []:
            self.player = subprocess.Popen([f"{uci_path}/{uci_executable}"] + args, cwd=uci_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        else:
            self.player = subprocess.Popen(f"{uci_path}/{uci_executable}", cwd=uci_path, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE)
        # self.player = subprocess.run()
        self.send("uci")
        self.wait_for_token("readyok")

        self.reset()

        self.update_board_position()

    def reset(self):
        print("UCI Reset")
        self.send("ucinewgame")
        self.wait_for_token("readyok")

    def update_board_position(self):
        # fen = self.board.generate_fen_string()
        fen = self.board.generate_move_fen()
        # self.send(f"position fen {fen}")
        self.send(fen)

    def my_turn(self):
        # If the last move made was the move being pondered, send ponderhit
        last_move = self.board.get_last_move()
        if last_move == self.ponder_move:
            self.send("ponderhit")
            time.sleep(self.think_time/2)
        else:
            self.update_board_position()
            self.send("go infinite")
            time.sleep(self.think_time)
        print(self.board.generate_fen_string())
        self.player.stdout.flush()
        self.send("stop")
        output = self.wait_for_token("bestmove")
        tokens = output.split(' ')
        move = tokens[1]
        source = move[:2].upper()
        dest = move[2:].upper()
        if len(dest) == 3:
            # The AI is upgrading a pawn. The last character is the piece to upgrade to
            selection = dest[2]
            dest = dest[:2]
            if selection == "Q":
                self.target_piece = "Queen"
            elif selection == "R":
                self.target_piece = "Rook"
            elif selection == "K":
                self.target_piece = "Knight"
            elif selection == "B":
                self.target_piece = "Bishop"
        self.make_move(source, dest)

    def upgrade_pawn(self, pawn):
        return self.target_piece

    def send(self, message):
        self.player.stdin.write(f"{message}\n".encode('utf-8'))
        self.player.stdin.flush()
        output = self.player.stdout.readline()
        # error = self.player.stderr.readline()
        error = None
        if output is not None:
            output = output.decode("utf-8")
        if error is not None:
            error = error.decode("utf-8")
        return output, error

    def wait_for_token(self, token):
        output_token = None
        while output_token != token:
            output, error = self.send("isready")
            output = output.strip()
            output_token = output.split(' ')[0]
        print(output)
        return output
