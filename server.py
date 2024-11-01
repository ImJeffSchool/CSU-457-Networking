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

# TCP Server code for the project
# Basic Server Setup:
# 1. Create a server-side application that listens for incoming client connections on a specified port.
# 2. Implement a mechanism to handle multiple client connections simultaneously.
# 3. Log connection and disconnection events.

gameInstance = Jeopardy.Jeopardy()

logging.basicConfig(filename='Server.log', level=logging.INFO)
selector = selectors.DefaultSelector() # Selector object to multiplex I/O operations

#HOST = '127.0.0.1'                     # The server's hostname or IP address to listen on all interfaces
#PORT = 54323                          # The port used by the server
MAX_NUM_CLIENTS = 4
# ^ Constants for now, but will be changed later

client_List = []

registryList = []

def clientMsgBlast(msgContent):
    # send to all clients at once
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

            #currSock = client.sock
            #serverBlstMsg = Message.Message(selector, currSock, client)
            print("Port, IP, client are: ", port, ipAddress, client)
            
            """
            JSONSerializableArray = gameInstance.questionsANDanswers.currentQuestionBoard
            JSONSerializableArray.toList()
            
            gameInstanceJson = {
                "liveGame" : gameInstance.liveGame,
                "currentPlayer": client.name,
                "QuestionBoard": JSONSerializableArray
            }
            """
            
            
            
            content = {
                "action": "Blast",
                "value": msgContent
            }
            
            #serverBlstMsg.set_server_request(content)
            
            
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
            #serverBlstMsg.response_created = True
            serverBlstMsg._recv_buffer += message
            #print("serverBlstMsg._recv_buffer is: ",serverBlstMsg._recv_buffer)
            

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
    # send to all clients at once
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

# Method for listening to incoming connections
def listening_Socket():
    listen_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    listen_Socket.bind((host, port))
    listen_Socket.listen()
    listen_Socket.setblocking(False)
    selector.register(listen_Socket, selectors.EVENT_READ, data=None)
    
    print(' Server is listening on: ', (host, port))
    logging.info(f" Server is listening on: {host}:{port}")

# Method for accepting incoming connections
def accept_connection(sock):
    #registryList.append(sock)
    connection, ipAddress = sock.accept()
    server_Events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #server_Data = types.SimpleNamespace(addr=ipAddress, input_Data=b"", output_Data=b"")
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
    turnPlayer = 1
    if gameInstance.round == 0:
        time.sleep(1)
        clientMsgBlast("Starting the game!")
        updateGameState()
        
        if message.updateSent == True:
            return
        
        turnMsg = "It is now player ", str(turnPlayer), "'s turn"
        clientMsgBlast(turnMsg)
        
        #player 1 has taken their turn 
        gameInstance.incrementRound()
        
        while gameInstance.round > 0:
            turnMsg = "It is now player ", str(turnPlayer), "'s turn"
            clientMsgBlast(turnMsg)
            
            gameInstance.incrementRound()
        
    return
    """
    isOver = False
    
    while not isOver:
        for player in gameInstance.playerList:
            pointsList = []
            pointsList.append(player.points)
        mostPoints = max(pointsList)
        pointsList.clear()

            
    #selector.close()
    """      

def checkIfGameOver():
    if gameInstance.getNumPlayers() < 2:
        return True
    if len(gameInstance.questionsANDanswers.currentQuestionBoard) == 0:
        return True
    return False
            
# Method for handling incoming data
def handling_Incoming_Data (key, value = None):
    message = key.data
    sock = key.fileobj
    # print("In server handle connect", repr(message))
    
    
    if message.responseSent == True:
        return
    # print(f"R/W/value Flag set to: {value}")
    if value & selectors.EVENT_READ:
        message.process_read_write(value)
        message.responseSent = True
        registryList.append(sock)
        selector.unregister(sock)

    if value & selectors.EVENT_WRITE:
        
        message.process_read_write(value)
        
        gameInstance.checkIfGameStart()
        if gameInstance.liveGame == True:
            startGame(message)
            #this logic is also the reason
            #p2 doesn't get a readied up message
            
        #else:
            """
            #print("repr of message: ", repr(message))
            content = "Waiting for more players to connect..."
            contentBytes = message._json_encode(content, "utf-8")
            
            jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": "text/json",
            "content-encoding": "utf-8",
            "content-length": len(contentBytes),
            }
            
            jsonheaderBytes = message._json_encode(jsonheader, "utf-8")
            message_hdr = struct.pack(">H", len(jsonheaderBytes))
            
            resp = message_hdr + jsonheaderBytes + contentBytes

            print("WHAT are we sending over: ", resp)
            
            message._send_buffer = resp
            message.sock.send(message._send_buffer)
            
            
            message.toggleReadWriteMode("r")
            """
    
    
    '''
    jsonObject = message.getJson()
    
    if jsonObject["action"] == "Ready":
        name = input("Creating a new player to the game! What is your name")
    '''    
        
        
    '''
    name = input("Creating a new player to the game! What is your name")
    givenPlayer = Player.Player(name)
    gameInstance.addPlayer(givenPlayer)
    numPlayers = gameInstance.getNumPlayers()

    if numPlayers < 2:
        print("Need to call create response and ask for more Ready requests here")
    '''
    
    
    '''
    if value & selectors.EVENT_READ:
        # Might need to increase buffer size based on data in the future?
        incoming_Data = socket.recv(1028)  
        if incoming_Data:
            data.output_Data += incoming_Data
        else:
            print(' Closing connection to: ', data.addr)
            logging.info(f" Closing connection to: {data.addr}")
            selector.unregister(socket)
            socket.close()
        
    if value & selectors.EVENT_WRITE:
        if data.output_Data:
            sent_Data = socket.send(data.output_Data)
            data.output_Data = data.output_Data[sent_Data:]
    '''
# Main method for the server

argv = sys.argv[1:]
try: 
    opts, args = getopt.getopt(argv, "i:p:hn") 
except (getopt.GetoptError, NameError): 
    print("please use python server.py -h if unfamiliar with the protocol")
    exit()
for opt, arg in opts: 
    if opt in ['-i']: 
        host = arg
    elif opt in ['-p']: 
        port = int(arg)
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