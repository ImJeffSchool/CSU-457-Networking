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
        self.hasTakenTurn = False

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

    def setReadyState(self, state):
        self.isReady = state

    def getReadyState(self):
        return self.isReady
    
    def getName(self):
        return self.name
    
    def setName(self, name):
        self.name = name

    def getPoints(self):
        return self.points
    
    def __repr__(self):
        return (f"Player: {self.name}\n"
              f"Points: {self.points}\n"
              f"isReady: {self.isReady}\n")
        