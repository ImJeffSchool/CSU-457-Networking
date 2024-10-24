class Player:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.request_queued = False
        self.request = None
        self.response = None
        self.isReady = False
        self.address = None
        self.port = None

    def _addPoints(self, points):
        self.points += points

    def _subPoints(self, points): 
        self.points -= points
        
    def setAddress(self, addr):
        self.address = addr
    
    def getAddress(self):
        return self.address
    
    def setPort(self, prt):
        self.port = prt
    
    def getPort(self):
        return self.port

    # def askQuestion(self, questionVal):
        # need to fill out for json

    def setReadyState(self, state):
        self.isReady = state

    def getReadyState(self):
        return self.isReady
    # def answerQuestion(self, answer):
        # need to fill out for json

    def __repr__(self):
        return (f"Player: {self.name}\n"
              f"Points: {self.points}\n"
              f"isReady: {self.isReady}\n")
        