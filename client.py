import sys
import socket
import selectors
import types
import traceback
import struct
import logging
import linecache
import Player
import Message
import time
import getopt

logging.basicConfig(filename='Client.log', level=logging.INFO)
sel = selectors.DefaultSelector()

def startConnection(host, port):
    "Starts and registers a socket with the server"
    serverAddress = (host, port)
    
    print('Starting connection to ', serverAddress)
    logging.info('Starting connection to '.join((host, str(port))))
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    errorNumber = sock.connect_ex(serverAddress)
    
    if errorNumber == 0 or errorNumber == 115 :
        print("You successfully connected to the server!\n")
    else:
        errorLine = linecache.getline('./resources/TCPErrorNumbers.txt', errorNumber)
        print('Unable to connect. Error code: ' + errorLine)
        logging.info('Unable to connect. Error code: ' + errorLine)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    
    message = Message.Message(sel, sock, serverAddress, role = 'client')
    sel.register(sock, events, data = message)
    return message

def create_request(action, value=None):
    common_dict = {
        "type": "text/json",
        "encoding": "utf-8"
    }

    if action == "Ready": common_dict["content"] = {"action": action}
    if value : common_dict["content"] = {"action": action, "value": value}

    return common_dict

#########################
#Parse Command line args
#########################
argv = sys.argv[1:]
try: 
    opts, args = getopt.getopt(argv, "i:p:hn") 
except (getopt.GetoptError, NameError): 
    print("please use python client.py -h if unfamiliar with the protocol")
    exit()

host = None
port = None

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
        
action = input("When you are ready to start the game please type \"Ready\"")
request = create_request(action)

message = startConnection(host, port)

try:
    while True:
        events = sel.select(timeout=None)
        for key, value in events:
            message = key.data
            try:
                message.process_read_write(value)
            except Exception as e:
                pass
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
    logging.info('caught keyboard interrupt, exiting')
finally:
    sel.close