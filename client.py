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

import selectors
import socket

def startConnection(host, port):
    """Starts and registers a socket with the server"""
    serverAddress = (host, port)

    print('Starting connection to ', serverAddress)
    logging.info('Starting connection to '.join((host, str(port))))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)  # Ensure non-blocking mode
    errorNumber = sock.connect_ex(serverAddress)

    if errorNumber == 0 or errorNumber == 115:
        print("Connection initiated, waiting for server response...\n")
        
        tmpSel = selectors.DefaultSelector()
        tmpSel.register(sock, selectors.EVENT_READ)

        # Wait for up to 0.2 seconds for a response from the server
        events = tmpSel.select(timeout=0.2)
        tmpSel.unregister(sock)

        if events:
            try:
                # Read the server's response if available
                response = sock.recv(1024).decode('utf-8')
                if "denied" in response.lower():
                    print(f"Connection denied by server: {response}")
                    sock.close()
                    exit()
                else:
                    print(f"Server response: {response}")
            except Exception as e:
                print(f"Error receiving server response: {e}")
                exit()
        else:
            print("Successfully connected to the Jeo-Jeopardy Lobby!")
    else:
        errorLine = linecache.getline('./resources/TCPErrorNumbers.txt', errorNumber)
        print('Unable to connect. Error code: ' + errorLine)
        logging.info('Unable to connect. Error code: ' + errorLine)
        exit()

    # Register the socket for normal operations
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = Message.Message(sel, sock, serverAddress, role='client')
    sel.register(sock, events, data=message)

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
        value = alldata[1]
    
    #################################
    #process the response from server
    #################################
        if action == "Ready":
            print(value, "Now waiting for other players...")
            message.toggleReadWriteMode("r")
        elif action == "Broadcast":
            if "The player with the most points is:" in value:
                print(value)
                exit()
            if "Now exiting" in value:
                print(value)
                exit()
            print(value)
            message.toggleReadWriteMode("r")
        elif action == "Update":
            #print("Player list is: ", message.response["Value"]["playerList"]
            print("Player scores are: ", value)
                
            message.toggleReadWriteMode('r')
        elif action == "YourTurn":
            print(message.response["Value"])
            value = input()
            if ',' in value:
                x,y = value.split(',')
                while (int(x) < 1 or int(x) >5) or (int(y) < 1 or int(y) > 5):
                    print("Row/Column number is invalid. Please choose numbers in the range of 1-5")
                    value = input()
                    x,y = value.split(',')
            
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
            if (message.response["Value"] == True):
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

        #if len(alldata) > 2:
        alldata = alldata[2:]
        #if len(alldata) == 2:
         #   alldata = None

        if value == "Quit": exit()
        action = None
        value = None

    #message.response = None

# Parse Command line args
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