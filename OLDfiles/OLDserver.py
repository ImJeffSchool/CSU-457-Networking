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

gameInstance = Jeopardy.Jeopardy()

logging.basicConfig(filename='Server.log', level=logging.INFO)
selector = selectors.DefaultSelector() # Selector object to multiplex I/O operations

MAX_NUM_CLIENTS = 2

client_List = []

registryList = []


def clientMsgBlast(msgContent):
    """send to all clients at once"""

    print("Into clientMsgBlast\n")
    for client in gameInstance.playerList:
        try:
            ipAddress = client.getAddress()
            port = client.getPort()
            
            serverBlstMsg = Message.Message(selector, port, ipAddress, role='server', gameInstance=gameInstance)
            server_Events = selectors.EVENT_READ | selectors.EVENT_WRITE
            
            try:
                selector.register(registryList.pop(0), server_Events, data=serverBlstMsg)
            except Exception as e:
                pass    

            print("Port, IP, client are: ", port, ipAddress, client)
            
            content = {
                "action": "Blast",
                "value": msgContent
            }
            
            contentBytes = serverBlstMsg._json_encode(content, "utf-8")
            jsonheader = {
                "byteorder": sys.byteorder,
                "content-type": "text/json",
                "content-encoding": "utf-8",
                "content-length": len(contentBytes),
            }
            jsonheaderBytes = serverBlstMsg._json_encode(jsonheader, "utf-8")
            messageHeader = struct.pack(">H", len(jsonheaderBytes))
            message = messageHeader + jsonheaderBytes + contentBytes
            serverBlstMsg._recv_buffer += message            

            if serverBlstMsg._jsonheader_len is None:
                serverBlstMsg.process_protoheader()

            if serverBlstMsg._jsonheader_len is not None:
                if serverBlstMsg.jsonheader is None:
                    serverBlstMsg.process_jsonheader()

            if serverBlstMsg.jsonheader:
                serverBlstMsg.process_message()

            serverBlstMsg.toggleReadWriteMode('w')
            serverBlstMsg.process_read_write(2)
      
        except Exception as e:
            print("error is: ", e)
            logging.info("Ran into trouble on the blast message")

def updateGameState():
    """send to all clients at once"""
    print("Into Update\n")
    playerList = []
    for client in gameInstance.playerList:
        try:
            ipAddress = client.getAddress()
            port = client.getPort()
            
            serverBlstMsg = Message.Message(selector, port, ipAddress, role='server', gameInstance=gameInstance)
            #server_Events = selectors.EVENT_READ | selectors.EVENT_WRITE
            
            #selector.register(registryList.pop(0), server_Events, data=serverBlstMsg)

            print("Port, IP, client are: ", port, ipAddress, client)
            
            '''
            JSONSerializableArray = gameInstance.questionsANDanswers.currentQuestionBoard
            JSONSerializableArray.toList()
            '''
            playerObj = {
                "name" : client.getName(),
                "points" : client.getPoints(),
            }
            
            playerList.append(playerObj)
            
            questionObj = {
                "CurrentBoard": gameInstance.questionsANDanswers.currentQuestionBoard
            }
            
            gameInstanceJson = {
                "liveGame" : gameInstance.liveGame,
                "currPlayer": playerObj,
                "QuestionBoard": questionObj
            }
            
            content = {
                "action": "Update",
                "value": gameInstanceJson
            }
            
            contentBytes = serverBlstMsg._json_encode(content, "utf-8")
            jsonheader = {
                "byteorder": sys.byteorder,
                "content-type": "text/json",
                "content-encoding": "utf-8",
                "content-length": len(contentBytes),
            }
            jsonheaderBytes = serverBlstMsg._json_encode(jsonheader, "utf-8")
            messageHeader = struct.pack(">H", len(jsonheaderBytes))
            message = messageHeader + jsonheaderBytes + contentBytes
            serverBlstMsg._recv_buffer += message           

            if serverBlstMsg._jsonheader_len is None:
                serverBlstMsg.process_protoheader()

            if serverBlstMsg._jsonheader_len is not None:
                if serverBlstMsg.jsonheader is None:
                    serverBlstMsg.process_jsonheader()

            if serverBlstMsg.jsonheader:
                serverBlstMsg.process_message()

            serverBlstMsg.toggleReadWriteMode('w')
            serverBlstMsg.process_read_write(2)

            
        except Exception as e:
            print("error is: ", e)
            logging.info("Ran into trouble on the update message")

def listening_Socket():
    """Method for listening to incoming connections"""
    listen_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    listen_Socket.bind((host, port))
    listen_Socket.listen()
    listen_Socket.setblocking(False)
    selector.register(listen_Socket, selectors.EVENT_READ, data=None)
    
    print(' Server is listening on: ', (host, port))
    logging.info(f" Server is listening on: {host}:{port}")

def accept_connection(sock):
    """Method for accepting incoming connections"""
    connection, ipAddress = sock.accept()
    server_Events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = Message.Message(selector, connection, ipAddress, role='server', gameInstance=gameInstance)

    connection.setblocking(False)
    selector.register(connection, server_Events, data=message)
    logging.info(f"Accepted connection from this client: {ipAddress}")

    client_List.append(message)
    currPlayer = Player.Player(("Player", (gameInstance.getNumPlayers()+1)))
    currPlayer.setAddress(ipAddress)
    currPlayer.setPort(connection)
    
    gameInstance.addPlayer(currPlayer)
    logging.info(f"Client list: {repr(client_List)}")
    print('Accepted connection from this client: ', ipAddress)
    
def startGame(message):
    """Starting main game logic once all players are ready"""
        
    if gameInstance.round == 0:
        turnPlayer = genInitialTurnPlayer()
        gameInstance.setTurnPlayer(turnPlayer)
        gameInstance.currentPlayer = gameInstance.playerList[turnPlayer-1]
        
        clientMsgBlast("Starting the game!")
        time.sleep(1)
        updateGameState()
        turnMsg = "It is now player ", str(turnPlayer), "'s turn"
        clientMsgBlast(turnMsg)
        
        #if gameInstance.round == 1:
        message = Message.Message(selector, gameInstance.currentPlayer.getPort(), gameInstance.currentPlayer.getAddress(), role='server', gameInstance=gameInstance)
        message.set_server_response(message.create_message_server({"Action": "YourTurn", "Value": str(gameInstance.playerList[turnPlayer-1].getAddress())}))
        message.create_message()
        message.process_read_write(2)
        message.toggleReadWriteMode("r")

    elif gameInstance.round != 0 and gameInstance.round %1 == 0:
        turnPlayer = determineNextTurn(gameInstance.getTurnPlayer())
        gameInstance.setTurnPlayer(turnPlayer)
        gameInstance.currentPlayer = gameInstance.playerList[turnPlayer-1]
        
        updateGameState()
        turnMsg = "It is now player ", str(turnPlayer), "'s turn"
        clientMsgBlast(turnMsg)
    
        message = Message.Message(selector, gameInstance.currentPlayer.getPort(), gameInstance.currentPlayer.getAddress(), role='server', gameInstance=gameInstance)
        message.set_server_response(message.create_message_server({"Action": "YourTurn", "Value": str(gameInstance.playerList[turnPlayer-1].getAddress())}))
        message.create_message()
        message.process_read_write(2)
        message.toggleReadWriteMode("r")
            
    gameInstance.incrementRound()        
    return
    #player 1 has taken their turn 
    #gameInstance.incrementRound()
    
    #turnPlayer = determineNextTurn(turnPlayer)
        
    return   

def writeYourTurnResponse():
    message = Message.Message(selector, gameInstance.currentPlayer.getPort(), gameInstance.currentPlayer.getAddress(), role='server', gameInstance=gameInstance)
    message.set_server_response(message.create_message_server({"Action": "YourTurn", "Value": str(gameInstance.playerList[gameInstance.turnPlayer-1].getAddress())}))
    message.create_message()
    message.process_read_write(2)
    message.toggleReadWriteMode("r")

def checkIfGameOver():
    """Check if the game is over..."""
    if gameInstance.getNumPlayers() < 2:
        return True
    if len(gameInstance.questionsANDanswers.currentQuestionBoard) == 0:
        return True
    return False
    
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

def handling_Incoming_Data (key, value = None):
    """Method for handling incoming data"""
    message = key.data
    sock = key.fileobj
    
    if message.responseSent == True:
        value = 1
    
    # print(f"R/W/value Flag set to: {value}")
    if value & selectors.EVENT_READ:
        message.process_read_write(value)
        message.responseSent = True
        
        try:
            if message.response["content"]["Action"] == "Ready":
                registryList.append(sock)
                selector.unregister(sock)
        except Exception:
            pass
        
        try:
            if message.response["content"]["Action"] == "ValidateAnswer":
                value = 2
        except Exception:
            pass
    try: 
        if message.response["content"]["Action"] == "SelectedQuestion":
            value = 2
    except Exception:
        pass
    
    if value & selectors.EVENT_WRITE:
        
        message.process_read_write(value)
        
        gameInstance.checkIfGameStart()
        if gameInstance.liveGame == True:
            startGame(message)
    
# Main method for the server
argv = sys.argv[1:]
try: 
    opts, args = getopt.getopt(argv, "i:p:hn") 
except (getopt.GetoptError, NameError): 
    print("please use python server.py -h if unfamiliar with the protocol")
    exit()
for opt, arg in opts: 
    if opt in ['-i']: host = arg
    elif opt in ['-p']: port = int(arg)
    elif opt in ['-h']:
        print("Use python server.py -i <IP ADDRESS> -p <PORT NUMBER> to run the program")
        exit()
    elif opt in ['-n']:
        print("The name of the DNS server is: CRAWFORD.ColoState.EDU")
        exit()

listening_Socket()

try:
    while True:
        events = selector.select(timeout=None)
        for key, value in events:
            if key.data is None:
                accept_connection(key.fileobj)
            else:
                # print("In loop:", repr(key))
                # print("In loop value event mask:", repr(value))
                handling_Incoming_Data(key, value)
except Exception as e:
    print(f"main: error: exception for {key.data.addr}:\n{traceback.format_exc()}")
    logging.info(f"main: error: exception for {key.data.addr}:\n{traceback.format_exc()}")
    client2rem = None
    for client in gameInstance.playerList:
        if client.getAddress() == key.data.addr: client2rem = client
    client_List.remove(client2rem)
    logging.info(f"Client list: {client_List}")
    key.fileobj.close()
except KeyboardInterrupt:   
    print("caught keyboard interrupt, exiting")
    logging.info("caught keyboard interrupt, exiting")
    logging.info(f"Client list: {client_List}") 
finally:
    selector.close()