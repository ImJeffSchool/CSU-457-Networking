import Player
import Question
import random

class Jeopardy:
    def __init__(self):
        self.liveGame = False
        self.playerList = []
        self.questionsANDanswers = Question.Question()
        self.round = 0
        self.playerGuess = None
        self.currentPlayer = None
        self.playerTurn = 0        

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
            if player.isReady: listOfReadyPlayers.append(player)
            
        if len(listOfReadyPlayers) == len(self.playerList):
            self.toggleLiveGame()
            
    def incrementRound(self):
        self.round += 0.5
    
    def setTurnPlayer(self, turnPlayer):
        self.turnPlayer = turnPlayer
    
    def getTurnPlayer(self):
        return self.turnPlayer

