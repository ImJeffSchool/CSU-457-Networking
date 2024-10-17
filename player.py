class Player:
    def __init__(self, name, points):
        self.name = name
        self.points = points
        self.request_queued = False
        self.request = None
        self.response = None

    def _addPoints(self, points):
        self.points += points

    def _subPoints(self, points): 
        self.points -= points

    def askQuestion(self, questionVal):
        # need to fill out for json

    def answerQuestion(self, answer):
        # need to fill out for json