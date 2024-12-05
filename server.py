import sys
import socket
import selectors
import types
import logging
import traceback
import Question
import Player
import Jeopardy
import Message
import struct
import getopt
import time
import random
import json

logging.basicConfig(filename='logs/Server.log', filemode='w', level=logging.INFO)
selector = selectors.DefaultSelector() 

host = '0.0.0.0'
MAX_NUM_CLIENTS = 2
client_List = []
messageList = []
sockList = []
gameInstance = Jeopardy.Jeopardy()

testGameOverArray = [
                        "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY",
                        "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY",
                        "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY",
                        "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY",
                        "EMPTY", "EMPTY", "EMPTY", "EMPTY", "EMPTY"
                    ]

def listening_socket():
    """Method for listening to incoming connections"""
    listen_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_Socket.bind((host, port))
    listen_Socket.listen()
    listen_Socket.setblocking(False)
    selector.register(listen_Socket, selectors.EVENT_READ, data=None)

    print('Server is listening on: ', (host, port))
    logging.info(f" Server is listening on: {host}:{port}")

def accept_connection(sock):
    """Method for accepting incoming connections"""
    sockOBJ, addrANDport = sock.accept()
    sockOBJ.setblocking(True)

    if len(gameInstance.playerList) == MAX_NUM_CLIENTS:
        try:
            sockOBJ.sendall(("Lobby connection denied. [Full Lobby]").encode('utf-8'))
            logging.info(f"Denied connectino from {addrANDport}: Lobby is full")
        except Exception as e:
            logging.error(f"Error sending denial message to {addrANDport}: {e}")
        finally:
            sockOBJ.close()
        return

    server_Events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = Message.Message(selector, sockOBJ, addrANDport, role='server', gameInstance=gameInstance)
    messageList.append(message)

    sockList.append(sockOBJ)
    selector.register(sockOBJ, server_Events, data=message)
    logging.info(f"Accepted connection from this client: {addrANDport}")

    client_List.append(message)
    currPlayer = Player.Player()
    currPlayer.set_addrANDport(addrANDport)
    currPlayer.set_sockOBJ(sockOBJ)
    gameInstance.addPlayer(currPlayer)

    logging.info(f"Client list: {repr(client_List)}")
    print(f"Accepting connection from client: {addrANDport}")

def handle_incoming_data(key, value=None):
    """Method for handling incoming data"""
    message = key.data
    sock = key.fileobj
        
    try:
        if value & selectors.EVENT_READ:
            return message.process_read_write(value)
        if value & selectors.EVENT_WRITE:
            message.process_read_write(value)
        return
    except RuntimeError as e:
        logging.info(f"Caught a RuntimeError in handle_incoming_data: {e}")
        selector.unregister(sock)
        sock.close()
        i = 1
        for player in gameInstance.playerList:
            if player.get_addrANDport() == message.addr:
                gameInstance.playerList.remove(player)
                stringMsg = "Player " + str(i) + " has disconnected unexpectedly"
                broadcastMsg(stringMsg, "Broadcast")
            i +=1
        
        checkInsufficientPlayers()
        #exit()

def processRequest(actionValue, message):
    x = None
    y = None
    if actionValue == None: 
        return
            
    action, value = actionValue.split(", ")

    if action == "Ready":
        for player in gameInstance.playerList:
            if player.get_addrANDport() == message.addr:
                player.setReadyState(True)
                player.set_name(value)
            response = {"Action": "Ready", "Value": "You are Ready-ed Up!"}
    elif action == "PlayerSelection":
        x, y = value.split(",")
        question = gameInstance.questionsANDanswers.currentQuestionBoard[int(x)-1][int(y)-1]
        gameInstance.playerGuess = int(x)-1, int(y)-1
        if question == "EMPTY":
            response = {"Action": "IndicateDuplicate", "Value": "Chosen question has already been answered. Now trying again"}
        else:
            response = {"Action": "SelectedQuestion", "Value": str(question)}
            messageList[gameInstance.currentPlayer-1].dontSendYourTurn = True
            gameInstance.questionsANDanswers.pprintBoard[int(x)-1][int(y)-1] = "Empty"
    elif action == "PlayerAnswer":
        x = gameInstance.playerGuess[0]
        y = gameInstance.playerGuess[1]
        response = {"Action": "ValidateAnswer", "Value": ""} 
        if value.lower() == (gameInstance.questionsANDanswers.currentAnswerList[int(x)][int(y)]).lower():
            gameInstance.questionsANDanswers.currentQuestionBoard[int(x)][int(y)] = "EMPTY"
            gameInstance.playerList[gameInstance.currentPlayer-1].add_points(gameInstance.questionsANDanswers.aValues[int(x)][int(y)])
            response["Value"] = True
            gameInstance.round += 0.5
            messageList[gameInstance.currentPlayer-1].dontSendYourTurn = False
            gameInstance.currentPlayer = determineNextTurn(gameInstance.currentPlayer)
        else:
            response["Value"] = False
            gameInstance.round += 0.5
            messageList[gameInstance.currentPlayer-1].dontSendYourTurn = False
            gameInstance.currentPlayer = determineNextTurn(gameInstance.currentPlayer)
            
    elif action == "Quit":
        stringMsg = "Player " + str(gameInstance.currentPlayer) + " has quit the game"
        broadcastMsg(stringMsg, "Broadcast")
        currSock = gameInstance.playerList[gameInstance.currentPlayer-1].get_sockOBJ()
        selector.unregister(currSock)
        currSock.close()
        gameInstance.playerList.remove(gameInstance.playerList[gameInstance.currentPlayer-1])
        checkInsufficientPlayers()
    
    elif action == "YesPlayAgain":
        print("They want to play again")
        
    message.response = message.create_server_message(response)
    message.create_message()
    message.toggleReadWriteMode('w')
    message.request = None
    message.write()
    if response["Action"] == "ValidateAnswer" and response["Value"] == True:
        coordPair =  "#" + str(x) + "," + str(y) + "," + gameInstance.playerList[gameInstance.currentPlayer-1].get_name()
        broadcastMsg(coordPair, "Broadcast")
    
def broadcastMsg(msgContent, action):
    "Send to all clients at once"
    print("Into broadcastMsg")
    
    for client in gameInstance.playerList:
        try:
            addrANDport = client.get_addrANDport()
            sockOBJ = client.get_sockOBJ()
            sockList.append(sockOBJ)
            serverBroadcastMsg = Message.Message(selector, sockOBJ, addrANDport, role='server', gameInstance=gameInstance)
            print("Port, IP, client are: ", sockOBJ, addrANDport, client)
            
            response = {
                "Action": action,
                "Value": msgContent
            }
            
            serverBroadcastMsg.response = serverBroadcastMsg.create_server_message(response)
            serverBroadcastMsg.create_message()
            serverBroadcastMsg.toggleReadWriteMode('w')
            serverBroadcastMsg.request = None
            serverBroadcastMsg.write()

        except Exception as e:
            print("error is: ", e)
            
def checkInsufficientPlayers():
    if len(gameInstance.playerList) <= 1:
            broadcastMsg("There are fewer than the required amount of players to run the game. Now exiting...", "Broadcast")
            exit()

def LiveGame():
    """Handles the game logic once all players have readied up"""
    if gameInstance.round == -1.0:
        gameInstance.round = 0.0
    if gameInstance.currentPlayer == None:
        gameInstance.currentPlayer = genInitialTurnPlayer()
    if gameInstance.round % 1 == 0.5: 
        currentMessageObj = messageList[gameInstance.currentPlayer-1]
        if currentMessageObj.dontSendYourTurn == False:
            player_name = gameInstance.playerList[gameInstance.currentPlayer-1].get_name()
            theBroadcastMsg = "It is now player "+ player_name + "'s turn."
            broadcastMsg(theBroadcastMsg, "Broadcast")
            #gameInstance.questionsANDanswers.currentQuestionBoard[gameInstance.playerGuess[0]][gameInstance.playerGuess[1]]
            response = {"Action": "YourTurn", "Value": "Choose a question. (Enter like <ColNumber,RowNumber>)"}
            currentMessageObj.response = currentMessageObj.create_server_message(response)
            currentMessageObj.create_message()
            currentMessageObj.toggleReadWriteMode('w')
            currentMessageObj.request = None
            currentMessageObj.write()
    elif gameInstance.round % 1 == 0:
        currentMessageObj = messageList[gameInstance.currentPlayer-1]
        
        if currentMessageObj.dontSendYourTurn == False:
            broadcastMsg(packGame(), "Update")
            player_name = gameInstance.playerList[gameInstance.currentPlayer-1].get_name()
            theBroadcastMsg = "It is now player "+ player_name + "'s turn."
            broadcastMsg(theBroadcastMsg, "Broadcast")
            response = {"Action": "YourTurn", "Value": "Choose a question. The game is a 5x5 grid with various questions. (Enter like <ColNumber,RowNumber>)"}
            currentMessageObj.response = currentMessageObj.create_server_message(response)
            currentMessageObj.create_message()
            currentMessageObj.toggleReadWriteMode('w')
            currentMessageObj.request = None
            currentMessageObj.write()
    if all(question == "EMPTY" for sublist in gameInstance.questionsANDanswers.currentQuestionBoard for question in sublist):
        GameOver()
    return

def GameOver():
    "Checks if the question board is empty, then assigns a winner and closes the server if this was the case"
    #testGameOverArray
    # ^^^^^ this test array makes it easier to test if game is over
    # gameInstance.questionsANDanswers.currentQuestionBoard
    # ^^^^ use for actual game over check
    broadcastMsg("Game over! Now determining the winner...", "Broadcast")
    mostPoints = gameInstance.playerList[0].get_points()
    bestPlayer = gameInstance.playerList[0]
    endMessage = ""
    for player in gameInstance.playerList:
        if player.get_points() > mostPoints:
            mostPoints = player.get_points()
            bestPlayer = player
        elif player.get_points() == mostPoints:
            endMessage = "There was a tie! Both " + bestPlayer.get_name() + " and " + player.get_name() + " have the same number of points!"
    endMessage = "The player with the most points is: " + bestPlayer.get_name() + " with " + str(mostPoints) + " points! " + bestPlayer.get_name() + " wins!" 
    broadcastMsg(endMessage, "Broadcast")


        #play again       
        # for message in messageList:
        #     response = {"Action": "AskPlayAgain", "Value": "Would you like to play again or would you like to quit?"}
        #     message.response = message.create_server_message(response)
        #     message.create_message()
        #     message.toggleReadWriteMode('w')
        #     message.request = None
        #     message.write()
        
        # for player in gameInstance.playerList:
        #     selector.unregister(player.get_addrANDport)
        # for sock in sockList:
        #     sock.close()   
    exit() 

def packGame():
    playerString = ""
    for player in gameInstance.playerList:
        # playerObj = {
        #     "name" : player.get_name(),
        #     "points" : player.get_points()
        # }
        playerString += (player.get_name() + ":" + str(player.get_points()) + ":")
    
    playerString = playerString[:-1]
    return playerString

def genInitialTurnPlayer():
    randNum = random.randint(1,MAX_NUM_CLIENTS)
    return randNum 

def determineNextTurn(currentTurn):
    nextTurn = 0
    if currentTurn+1 > MAX_NUM_CLIENTS:
        nextTurn = 1
    else:
        nextTurn = currentTurn+1
    return nextTurn

argv = sys.argv[1:]
try: 
    opts, args = getopt.getopt(argv, "p:hn") 
except (getopt.GetoptError, NameError): 
    print("please use python server.py -h if unfamiliar with the protocol")
    exit()
for opt, arg in opts: 
    if opt in ['-p']: 
        port = int(arg)
    elif opt in ['-h']:
        print("Use python server.py -p <PORT NUMBER> to run the program")
        exit()
    elif opt in ['-n']:
        print("The name of the DNS server is: CRAWFORD.ColoState.EDU")
        exit()

listening_socket()

try:
    while True:
        events = selector.select(timeout=None)
        for key, value in events:
            if key.data is None: 
                accept_connection(key.fileobj)
            # Need to figure out the correct elif to not call processRequest unless game data is in Message
            elif len(gameInstance.playerList) == MAX_NUM_CLIENTS:     
                processRequest(handle_incoming_data(key, value), key.data)
                gameInstance.checkIfGameStart()
                if gameInstance.liveGame == True:
                    if gameInstance.round == -1.0: broadcastMsg("Game is about to start...", "Broadcast")
                    LiveGame()
except Exception as e:
    logging.info(f"main: error: exception for{key.data.addr}:\n{traceback.format_exc()}")
    print(f"main: error: exception for {key.data.addr}:\n{traceback.format_exc()}")
    key.fileobj.close()
except KeyboardInterrupt:
    logging.info("caught keyboard interrupt, exiting")
    print("caught keyboard interrupt, exiting")
finally: 
    selector.close()