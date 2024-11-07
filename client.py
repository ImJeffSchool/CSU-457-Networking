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

logging.basicConfig(filename='logs/Client.log', level=logging.INFO)
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

    if action == "Ready": common_dict["Content"] = {"Action": action, "Value": value}
    if value : common_dict["Content"] = {"Action": action, "Value": value}

    return common_dict

def process_response(actionValue, message):
    if actionValue == None: 
        return
    
    alldata = actionValue.split(", ")

    while alldata:
        action = alldata[0]
        if action == "Update":
            value = alldata[1:]
        else:
            value = alldata[1]
    
    #################################
    #process the response from server
    #################################
        if action == "Ready":
            print(value, "Now waiting for other players...")
            message.toggleReadWriteMode("r")
        elif action == "Broadcast":
            print(value)
            message.toggleReadWriteMode("r")
        elif action == "Update":
            print("Updating gameInstance with: ", value)
            message.toggleReadWriteMode('r')

        alldata = alldata[2:]
    #message.response = None

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

try:
    message = startConnection(host, port)
    action, value = input("When you are ready to start the game please type \"Ready\" and your name, separated with a single comma and space ").split(", ")
    request = create_request(action, value)
    message.set_client_request(request)
    message.write()
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
    logging.info('caught keyboard interrupt, exiting')

try:
    while True:
        events = sel.select(timeout=None)
        for key, value in events:
            #message = key.data
            try:
                process_response(message.process_read_write(value), message)
            except Exception as e:
                pass
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
    logging.info('caught keyboard interrupt, exiting')
finally:
    sel.close