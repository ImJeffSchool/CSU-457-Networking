import sys
import socket
import selectors
import types
import traceback
import struct
import logging

import TCPServer

# TCP Client code for the project
Static_HOST = '0.0.0.0'
Static_PORT = 54321

logging.basicConfig(filename='Client.log', level=logging.INFO)

sel = selectors.DefaultSelector()


def startConnection(Static_HOST, Static_PORT):
    serverAddress = (Static_HOST, Static_PORT)
    print('Starting connection to ', serverAddress)
    logging.info('Starting connection to ', serverAddress)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    errorNumber = sock.connect_ex(serverAddress)
    if errorNumber == 0 :
        print("IDK WHAT TO PUT HERE")
    elif errorNumber == 1:
        print('Unable to connect. Error code: ', errorNumber)
        logging.info('Unable to connect. Error code: ', errorNumber)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message1 = input("Enter a message you would like to send to the server")
    message1.encode()
    message2 = input("Enter another message you would like to send to the server")
    message2.encode()
    messages = [message1, message2]
    sel.register(sock, events, data = messages)
    

startConnection(Static_HOST, Static_PORT)


