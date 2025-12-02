class PlayerConfig:
    def __init__(self):
        self.human = False
        self.engine = "maia1100.py"

    def set_engine(self, engine):
        self.engine = engine

class Engine:
    def __init__(self, name, elo, path):
        self.name = name
        self.elo = elo
        self.path = path