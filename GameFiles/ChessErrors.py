class OutOfRange(Exception):

    def __init__(self):
        super().__init__("Invalid Square")


class PawnUpgrade(Exception):

    def __init__(self):
        super().__init__("Last Pawn Checked needs Upgraded")


class Check(Exception):

    def __init__(self):
        super().__init__("Check")


class Checkmate(Exception):

    def __init__(self, winner):
        self.winner = winner
        super().__init__(f"Checkmate! {winner} wins!")


class InvalidMove(Exception):

    def __init__(self, target, valid):
        super().__init__(f"{target} is not a valid move for that piece. Must be one of {valid}")


class TeamError(Exception):

    def __init__(self, team):
        super().__init__(f'{team} is not a valid chess team')


class TurnError(Exception):

    def __init__(self, current_team):
        super().__init__(f"It is {current_team}'s turn!")


class UnknownSquare(Exception):

    def __init__(self, attempt):
        super().__init__(f'"{attempt}" is not a valid chess square. Inputs must be between A1 and H8')


class PlayerError(Exception):

    def __init__(self):
        super().__init__(f"Too many players added to the game!")


class Stalemate(Exception):

    def __init__(self):
        super().__init__("Stalemate! Its a tie!")
