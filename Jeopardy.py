import Player
import Question

class Jeopardy:
    def __init__(self):
        self.liveGame = False
        self.playerList = []
        self.qList = []

    def toggleLiveGame(self):
        self.liveGame = True if not self.liveGame else self.liveGame = False

    def addPlayer(self, player):
        self.playerList.add(player)