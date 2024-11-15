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
import Jeopardy

logging.basicConfig(filename='logs/Client.log', filemode='w', level=logging.INFO)
sel = selectors.DefaultSelector()
gameInstance = Jeopardy.Jeopardy()
validSelections = [
                    "1,1", "1,2", "1,3", "1,4", "1,5",
                    "2,1", "2,2", "2,3", "2,4", "2,5",
                    "3,1", "3,2", "3,3", "3,4", "3,5",
                    "4,1", "4,2", "4,3", "4,4", "4,5",
                    "5,1", "5,2", "5,3", "5,4", "5,5",
                ]

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
    if action == "Quit": common_dict["Content"] = {"Action": action, "Value": value}
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
            print("Player list is: ", message.response["Value"]["playerList"])
            time.sleep(1)
            print("QuestionBoard is ", message.response["Value"]["QuestionBoard"]["CurrentBoard"])
            message.toggleReadWriteMode('r')
        elif action == "YourTurn":
            print(message.response["Value"])
            value = input()
            while value != "Quit" and value not in validSelections:
                print("Invalid selection! Please choose a row number and a col number between 1 and 5")
                value = input()
            if value == "Quit":
                request = create_request(action=value, value="")
            else:
                action = "PlayerSelection"
                request = create_request(action, value)
            message.set_client_request(request)
            message.write()
        elif action == "SelectedQuestion":
            print("Please answer this question: \n", message.response["Value"])
            value = input()
            if value == "Quit":
                request = create_request(action=value, value="")
            else:
                action = "PlayerAnswer"
                request = create_request(action, value)
            message.set_client_request(request)
            message.write()
        elif action == "ValidateAnswer":
            if (message.response["Value"]):
                print("You got it right")
            else:
                print("You got it wrong!")
        elif action == "AskPlayAgain":
            print(message.response["Value"])
            value = input()
            if value == "Quit":
                request = create_request(action=value, value="")
            else:
                action = "YesPlayAgain"
                request = create_request(action, value)
            message.set_client_request(request)
            message.write()

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