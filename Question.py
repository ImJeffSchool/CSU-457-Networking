import numpy as np
import random

class Question:
    def __init__(self):
        self.questionBoard1 = np.array((
                            ["Question1", "Question2", "Question3", "Question4", "Question5"],
                            ["Question6", "Question7", "Question8", "Question9", "Question10"],
                            ["Question11", "Question12", "Question13", "Question14", "Question15"],
                            ["Question16", "Question17", "Question18", "Question19", "Question20"],
                            ["Question21", "Question22", "Question23", "Question24", "Question25"],
                            ))
        
        self.questionBoard2 = np.array((
                            ["Question26", "Question27", "Question28", "Question29", "Question30"],
                            ["Question31", "Question32", "Question33", "Question34", "Question35"],
                            ["Question36", "Question37", "Question38", "Question39", "Question40"],
                            ["Question41", "Question42", "Question43", "Question44", "Question45"],
                            ["Question46", "Question47", "Question48", "Question49", "Question50"],
                            ))
        self.aList1 = np.array((
                            ["Answer", "Answer", "Answer", "Answer", "Answer"],
                            ["Answer", "Answer", "Answer", "Answer", "Answer"],
                            ["Answer", "Answer", "Answer", "Answer", "Answer"],
                            ["Answer", "Answer", "Answer", "Answer", "Answer"],
                            ["Answer", "Answer", "Answer", "Answer", "Answer"],
                            ))
        self.aList2 = np.array((
                            ["Answer", "Answer", "Answer", "Answer", "Answer"],
                            ["Answer", "Answer", "Answer", "Answer", "Answer"],
                            ["Answer", "Answer", "Answer", "Answer", "Answer"],
                            ["Answer", "Answer", "Answer", "Answer", "Answer"],
                            ["Answer", "Answer", "Answer", "Answer", "Answer"],
                            ))
        self.currentQuestionBoard = np.array([])
        self.chooseRandomQuestionBank()
        
    def chooseRandomQuestionBank(self):
        randNum = random.randint(1,2)
        if randNum == 1:
            self.currentQuestionBoard = self.questionBoard1
            self.currentAnswerList = self.aList1
        elif randNum == 2:
            self.currentQuestionBoard = self.questionBoard2
            self.currentAnswerList = self.aList2
            
    def printQuestionBoard(self):
        print(self.currentQuestionBoard)
        