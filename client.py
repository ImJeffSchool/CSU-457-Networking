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

# TCP Client code for the project
#Static_HOST = '127.0.0.1'
#Static_PORT = 54322

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

def startConnection(host, port):
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
        print("python client.py -i <IP ADDRESS> -p <PORT NUMBER>")
        exit()
    elif opt in ['-n']:
        print("The name of the DNS server is: CRAWFORD.ColoState.EDU")
        exit()



action = input("Please ready up with \"Ready\" or choose one of the options listed: ")
request = create_request(action)

#host, port = sys.argv[2], sys.argv[4]
#dashI, dashP = sys.argv[1], sys.argv[3]


message = startConnection(host, port)
message.set_client_request(request)

try:
    while True:
        events = sel.select(timeout=1)  
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