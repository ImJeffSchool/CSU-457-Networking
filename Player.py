class Player:
    def __init__(self):
        self.name = None
        self.points = 0
        self.isReady = False
        self.addrANDport = None
        self.sockOBJ = None
        self.hasTakenTurn = False

    def add_points(self, points):
        self.points += points

    def sub_points(self, points): 
        self.points -= points

    def get_points(self):
        return self.points

    def set_addrANDport(self, addr):
        self.addrANDport = addr

    def get_addrANDport(self):
        return self.addrANDport

    def set_sockOBJ(self, sockobj):
        self.sockOBJ = sockobj

    def get_sockOBJ(self):
        return self.sockOBJ

    def setReadyState(self, state):
        self.isReady = state

    def getReadyState(self):
        return self.isReady

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def __repr__(self):
        return (f"Player: {self.name}\n"
              f"Points: {self.points}\n"
              f"isReady: {self.isReady}\n")