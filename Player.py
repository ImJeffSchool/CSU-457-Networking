class Player:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.request_queued = False
        self.request = None
        self.response = None
        self.isReady = False

    def _addPoints(self, points):
        self.points += points

    def _subPoints(self, points): 
        self.points -= points

    # def askQuestion(self, questionVal):
        # need to fill out for json

    def toggleReady(self):
        if self.isReady == False: self.isReady = True
        else: self.isReady = False 

    # def answerQuestion(self, answer):
        # need to fill out for json
        