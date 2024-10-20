import sys
import socket
import selectors
import types
import logging
import traceback
import Question
import Player
import Jeopardy
import ServerMessaging
import struct

# TCP Server code for the project
# Basic Server Setup:
# 1. Create a server-side application that listens for incoming client connections on a specified port.
# 2. Implement a mechanism to handle multiple client connections simultaneously.
# 3. Log connection and disconnection events.

currentBoard = Question.Question()
currentBoard.chooseRandomQuestionBank()

gameInstance = Jeopardy.Jeopardy()

logging.basicConfig(filename='Server.log', level=logging.INFO)
selector = selectors.DefaultSelector() # Selector object to multiplex I/O operations

HOST = '127.0.0.1'                     # The server's hostname or IP address to listen on all interfaces
PORT = 54321                           # The port used by the server
MAX_NUM_CLIENTS = 4
# ^ Constants for now, but will be changed later

client_List = []

# Method for listening to incoming connections
def listening_Socket():
    listen_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    listen_Socket.bind((HOST, PORT))
    listen_Socket.listen()
    listen_Socket.setblocking(False)
    selector.register(listen_Socket, selectors.EVENT_READ, data=None)
    
    print(' Server is listening on: ', (HOST, PORT))
    logging.info(f" Server is listening on: {HOST}:{PORT}")

# Method for accepting incoming connections
def accept_connection(sock):
    connection, ipAddress = sock.accept()
    server_Events = selectors.EVENT_READ | selectors.EVENT_WRITE
    #server_Data = types.SimpleNamespace(addr=ipAddress, input_Data=b"", output_Data=b"")
    message = ServerMessaging.Message(selector, connection, ipAddress)
    
    connection.setblocking(False)
    client_List.append(ipAddress)
    logging.info(f"Client list: {client_List}")
    print('Accepted connection from this client: ', ipAddress)
    logging.info(f"Accepted connection from this client: {ipAddress}")
    selector.register(connection, server_Events, data=message)
    
    numPlayers = gameInstance.getNumPlayers()
    givenPlayer = Player.Player("Player" + str(numPlayers+1))
    gameInstance.addPlayer(givenPlayer)
    numPlayers = gameInstance.getNumPlayers()
    
    
    
def startGame():
    print("Game would start here")
    
        
# Method for handling incoming data
def handling_Incoming_Data (key, value = None):
    message = key.data
    
    if value & selectors.EVENT_READ:
        message.processReadWrite(value)

    if value & selectors.EVENT_WRITE:
        if gameInstance.getNumPlayers == 2:
            gameInstance.toggleLiveGame()
        
        if gameInstance.liveGame == False:
            message.processReadWrite(value)
        else:
            startGame()
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
listening_Socket()

try:
    while True:
        events = selector.select(timeout=None)
        for key, value in events:
            if key.data is None:
                accept_connection(key.fileobj)
            else:
                handling_Incoming_Data(key, value)
except Exception as e:
    print(f"main: error: exception for {key.data.addr}:\n{traceback.format_exc()}")
    logging.info(f"main: error: exception for {key.data.addr}:\n{traceback.format_exc()}")
    client_List.remove(key.data.addr)
    logging.info(f"Client list: {client_List}")
    key.fileobj.close()
except KeyboardInterrupt:   
    print("caught keyboard interrupt, exiting")
    logging.info("caught keyboard interrupt, exiting")
    logging.info(f"Client list: {client_List}") 
finally:
    selector.close()