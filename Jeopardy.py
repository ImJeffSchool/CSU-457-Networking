import Player
import Question

class Jeopardy:
    def __init__(self):
        self.liveGame = False
        self.playerList = []
        self.questionsANDanswers = Question.Question()

    def toggleLiveGame(self):
        if self.liveGame == False: self.liveGame = True
        else: self.liveGame = False

    def addPlayer(self, player):
        self.playerList.append(player)
        
    def getNumPlayers(self):
        return len(self.playerList)