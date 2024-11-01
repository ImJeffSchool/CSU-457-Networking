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
        try:
            incoming_data = key.fileobj.recv(1024)
            if incoming_data:
                print(f"Received message: {incoming_data.decode('utf-8')}")
                message.processReadWrite(value)
            else:
                print("closing connection to", message.addr)
                logging.info('closing connection to'.join(message.addr))
                sel.unregister(key.fileobj)
                key.fileobj.close()
        except Exception as e:
            print(f"Error reading from {message.addr}: {e}")
            logging.info(f"Error reading from {message.addr}: {e}")
            sel.unregister(key.fileobj)
            key.fileobj.close()
    if value & selectors.EVENT_WRITE:
        if message.outboundMessage:
            sent = key.fileobj.send(message.outboundMessage)
            message.outboundMessage = message.outboundMessage[sent:]

def create_request(action, value=None):
    return action.encode('utf-8')

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
        print("Use python server.py -i <IP ADDRESS> -p <PORT NUMBER> to run the program")
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
              handling_Incoming_Data(key, value)
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()