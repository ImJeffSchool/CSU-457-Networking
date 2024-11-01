import Player
import Question

class Jeopardy:
    def __init__(self):
        self.liveGame = False
        self.playerList = []
        self.questionsANDanswers = Question.Question()
        self.round = 0

    def toggleLiveGame(self):
        if self.liveGame == False: self.liveGame = True
        else: self.liveGame = False

    def addPlayer(self, player):
        self.playerList.append(player)
        
    def getNumPlayers(self):
        return len(self.playerList)
    
    def checkIfGameStart(self):
        if self.liveGame == True:
            return
        listOfReadyPlayers = []
        for player in self.playerList:
            listOfReadyPlayers.append(player.isReady)
            
        if all(listOfReadyPlayers) == True and len(listOfReadyPlayers) > 1:
            self.toggleLiveGame()
            
    def incrementRound(self):
        self.round += 1
