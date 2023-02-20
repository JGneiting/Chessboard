class OutOfRange(Exception):

    def __init__(self):
        super().__init__("Invalid Square")


class PawnUpgrade(Exception):

    def __init__(self):
        super().__init__("Last Pawn Checked needs Upgraded")


class Check(Exception):

    def __init__(self, aggressor):
        self.interest_piece = aggressor
        super().__init__("Check")
