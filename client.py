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

# TCP Client code for the project
Static_HOST = '127.0.0.1'
Static_PORT = 54322

logging.basicConfig(filename='Client.log', level=logging.INFO)
sel = selectors.DefaultSelector()

def handling_Incoming_Data(key, value = None) :
    message = key.data
    
    if value & selectors.EVENT_READ:
        #print("repr of message obj (client): ", repr(message))
        message.processReadWrite(value)
    if value & selectors.EVENT_WRITE:
        message.processReadWrite(value)
        print("Do another create request and send it off")

def create_request(action, value=None):
    common_dict = {
        "type": "text/json",
        "encoding": "utf-8"
    }

    if action == "Ready": common_dict["content"] = {"action": action}
    elif action == "-i": common_dict["content"] = {"action": action}
    elif action == "-p": common_dict["content"] = {"action": action}
    elif action == "-n": common_dict["content"] = {"action": action}
    elif action == "-h": common_dict["content"] = {"action": action}
    if value : 
        common_dict["content"] = {"action": action, "value": value}
        
    #print(common_dict)
    #else: common_dict["content"] = {"action": action, "value": value}

    return common_dict

def startConnection(Static_HOST, Static_PORT):
    serverAddress = (Static_HOST, Static_PORT)
    
    print('Starting connection to ', serverAddress)
    logging.info('Starting connection to '.join((Static_HOST, str(Static_PORT))))
    
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
    
print("Welcome! Let's get you connected. \n"
        + "Here are some options if you need help\n"
        + "-h for help on how to connect and play\n"
        + "-i for the ip address of the server\n"
        + "-p for the listening port of the server\n"
        + "-n for the DNS name of the server\n")

action = input("Please ready up with \"Ready\" or choose one of the options listed: ")
request = create_request(action)
    
message = startConnection(Static_HOST, Static_PORT)
message.set_client_request(request)

try:
    prevEvents = None
    while True:
        events = sel.select(timeout=1)
        if events != prevEvents:    
            for key, value in events:
                message = key.data
                try:
                    # if not message.request:
                    #     action = input("Please enter another command, or when you are ready, enter ready: ")
                    #     request = create_request(action)
                    #     message.set_client_request(request)
                    
                    message.process_read_write(value)
                    #handling_Incoming_Data(key, value)
                except Exception as e:
                    time.sleep(1)
            prevEvents = events
                #print(f"Exception: {e} was caught!\n")
           #     print(
            #        "main: error: exception for",
             #       f"{message.addr}:\n{traceback.format_exc()}",
             #   )
            #    logging.info('main: error: exception for'.join(message.addr, str(traceback.format_exc())))
                #message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
    logging.info('caught keyboard interrupt, exiting')
finally:
    sel.close