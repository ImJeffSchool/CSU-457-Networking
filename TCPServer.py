import sys
import socket
import selectors
import types

# TCP Server code for the project
# Basic Server Setup:
# 1. Create a server-side application that listens for incoming client connections on a specified port.
# 2. Implement a mechanism to handle multiple client connections simultaneously.
# 3. Log connection and disconnection events.

selector = selectors.DefaultSelector()

HOST = '127.0.0.1' # The server's hostname or IP address to listen on all interfaces
PORT = 54321       # The port used by the server

def accept_connection(sock):
    connection, ipAddress = sock.accept()
    server_Events = selectors.EVENT_READ | selectors.EVENT_WRITE
    server_Data = types.SimpleNamespace(addr=ipAddress, input_Data=b"", output_Data=b"")
    
    connection.setblocking(False)
    print('Accepted connection from this client: ', ipAddress)
    selector.register(connection, server_Events, data=server_Data)