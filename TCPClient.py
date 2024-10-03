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


sel = selectors.DefaultSelector()


def startConnection(Static_HOST, Static_PORT):
    serverAddress = (Static_HOST, Static_PORT)
    print("starting connection to", serverAddress)
    logging.basicConfig(filename='Client.log', level=logging.INFO)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(serverAddress)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message1 = input("Enter a message you would like to send to the server")
    message1.encode()
    message2 = input("Enter another message you would like to send to the server")
    message2.encode()
    messages = [message1, message2]
    sel.register(sock, events, data = messages)
    
    
startConnection(Static_HOST, Static_PORT)


