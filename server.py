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

# Selector object to multiplex I/O operations & logging for file
logging.basicConfig(filename='logs/Server.log', level=logging.INFO)
selector = selectors.DefaultSelector() 

MAX_NUM_CLIENTS = 2
client_List = []
registryList = []
gameInstance = Jeopardy.Jeopardy()

def listening_socket():
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
    sockOBJ, addrANDport = sock.accept()
    server_Events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = Message.Message(selector, sockOBJ, addrANDport, role='server', gameInstance=gameInstance)

    sockOBJ.setblocking(True)
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
        print(f"Caught a RuntimeError in handle_incoming_data: {e}")
        selector.unregister(sock)
        sock.close()
        exit()

def processRequest(actionValue, message):
    if actionValue == None: 
        return
    
    action, value = actionValue.split(", ")

    if action == "Ready":
        for player in gameInstance.playerList:
            if player.get_addrANDport() == message.addr:
                player.setReadyState(True)
                player.setName(value)
            response = {"Action": "Ready", "Value": "You are Ready-ed Up!"}
    #actionValue = action + "," + value

    message.response = message.create_server_message(response)
    message.create_message()
    message.toggleReadWriteMode('w')
    message.request = None
    message.write()

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
except Exception as e:
    logging.info(f"main: error: exception for{key.data.addr}:\n{traceback.format_exc()}")
    print(f"main: error: exception for {key.data.addr}:\n{traceback.format_exc()}")
    key.fileobj.close()
except KeyboardInterrupt:
    logging.info("caught keyboard interrupt, exiting")
    print("caught keyboard interrupt, exiting")
finally: 
    selector.close()