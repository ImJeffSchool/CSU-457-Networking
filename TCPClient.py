import sys
import socket
import selectors
import types
import traceback
import struct
import logging
import linecache

import ClientMessaging

# TCP Client code for the project
Static_HOST = '127.0.0.1'
Static_PORT = 54321

logging.basicConfig(filename='Client.log', level=logging.INFO)

sel = selectors.DefaultSelector()

def startConnection(Static_HOST, Static_PORT):
    serverAddress = (Static_HOST, Static_PORT)
    print('Starting connection to ', serverAddress)
    logging.info('Starting connection to '.join((Static_HOST, str(Static_PORT))))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    errorNumber = sock.connect_ex(serverAddress)
    if errorNumber == 0 or errorNumber == 115 :
        print("Operation succeeded") if errorNumber == 0 else print("Operation now in progress")
    else:
        errorLine = linecache.getline('./resources/TCPErrorNumbers.txt', errorNumber)
        print('Unable to connect. Error code: ' + errorLine)
        logging.info('Unable to connect. Error code: ' + errorLine)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    
    messages = ClientMessaging.Message(sel, sock, serverAddress)
    messages.createMessage()
    sel.register(sock, events, data = messages)
    
startConnection(Static_HOST, Static_PORT)

try:
    while True:
        events = sel.select(timeout=1)
        for key, value in events:
            message = key.data
            try:
                message.processReadWrite(value)
            except Exception:
                print(
                    "main: error: exception for",
                    f"{message.addr}:\n{traceback.format_exc()}",
                )
                logging.info('main: error: exception for' .join(message.addr, str(traceback.format_exc())))
                message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
    logging.info('caught keyboard interrupt, exiting')
finally:
    sel.close