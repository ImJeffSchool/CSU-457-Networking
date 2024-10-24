import numpy as np
import random


class Question:
    def __init__(self):
        self.questionBoard1 = np.array((
                            ["What is the capital of Canada?", "What planet is known as the Red Planet?", "Who was the first president of the United States?", "Who directed “Jurassic Park”?", "Who is known as the King of Pop?"],
                            ["What country won the 2018 FIFA World Cup?", "In which TV show would you find the character Walter White?", "Who painted the “Mona Lisa”?", "What is the largest mammal on Earth?", "Who was the king of the Greek gods?"],
                            ["What is the closest star to Earth?", "What is the chemical symbol for water?", "What is the value of pi to two decimal places?", "Who was assassinated on November 22, 1963?", "What element does “O” represent on the periodic table?"],
                            ["What sport is known as “America’s pastime”?", "What animated movie features a talking snowman named Olaf?", "What year did the Titanic sink?", "Who is the Roman god of war?", "Which 1994 film stars Tom Hanks as a man with a low IQ?"],
                            ["What river flows through Egypt?", "What is the fastest land animal?", "What social media platform is known for 280-character messages?", "Who was the British prime minister during most of World War II?", "What is the center of an atom called?"],
                            ))
        
        self.questionBoard2 = np.array((
                            ["Which country is both an island and a continent?", "What legendary rock band was Freddie Mercury a part of?", "What is a group of lions called?", "What famous wall was torn down in 1989?", "What movie features a computer system called Skynet?"],
                            ["What is the largest ocean on Earth?", "What mythical creature is half man, half horse?", "What does “HTTP” stand for in a web address?", "What is the capital of Japan?", "What is the hardest natural substance on Earth?"],
                            ["Who was the first woman to fly solo across the Atlantic Ocean?", "Which movie features the character Jack Sparrow?", "What artist is known for cutting off his own ear?", "What bird is often associated with delivering babies?", "Who is the Norse god of thunder?"],
                            ["What is the largest planet in our solar system?", "What is the chemical symbol for iron?", "What is the square root of 144?", "What company makes the iPhone?", "Who played Iron Man in the Marvel Cinematic Universe?"],
                            ["Who was the first man to walk on the moon?", "What is the largest country in the world by area?", "Who is the Greek god of the sea?", "What gas do humans exhale?", "What is the tallest mountain in the world?"],
                            ))
        self.aList1 = np.array((
                            ["Ottawa", "Mars", "George Washington", "Steven Spielberg", "Michael Jackson"],
                            ["France", "Breaking Bad", "Leonardo da Vinci", "Blue Whale", "Zeus"],
                            ["Sun", "H2O", "3.14", "John F. Kennedy", "Oxygen"],
                            ["Baseball", "Frozen", "1912", "Mars", "Forrest Gump"],
                            ["Nile River", "Cheetah", "Twitter", "Winston Churchill", "The nucleus"],
                            ))
        self.aList2 = np.array((
                            ["Australia", "Queen", "A pride", "The Berlin Wall", "The Terminator"],
                            ["The Pacific Ocean", "Centaur", "HyperText Transfer Protocol", "Tokyo", "Diamond"],
                            ["Amelia Earhart", "Pirates of the Caribbean", "Vincent van Gogh", "Stork", "Thor"],
                            ["Jupiter", "Fe", "12", "Apple", "Robert Downey Jr."],
                            [" Neil Armstrong", "Russia", "Poseidon", "Carbon dioxide", "Mount Everest"],
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
        