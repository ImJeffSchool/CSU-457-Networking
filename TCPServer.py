import sys
import socket
import selectors
import types
import logging
import traceback

# TCP Server code for the project
# Basic Server Setup:
# 1. Create a server-side application that listens for incoming client connections on a specified port.
# 2. Implement a mechanism to handle multiple client connections simultaneously.
# 3. Log connection and disconnection events.

logging.basicConfig(filename='Server.log', level=logging.INFO)
selector = selectors.DefaultSelector() # Selector object to multiplex I/O operations

HOST = '127.0.0.1'                     # The server's hostname or IP address to listen on all interfaces
PORT = 54321                           # The port used by the server
# ^ Constants for now, but will be changed later

# Method for listening to incoming connections
def listening_Socket():
    listen_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    listen_Socket.bind((HOST, PORT))
    listen_Socket.listen()
    listen_Socket.setblocking(False)
    selector.register(listen_Socket, selectors.EVENT_READ, data=None)
    
    print('Server is listening on: ', (HOST, PORT))
    logging.info("Server is listening on: ".join((HOST, str(PORT))))

# Method for accepting incoming connections
def accept_connection(sock):
    connection, ipAddress = sock.accept()
    server_Events = selectors.EVENT_READ | selectors.EVENT_WRITE
    server_Data = types.SimpleNamespace(addr=ipAddress, input_Data=b"", output_Data=b"")
    
    connection.setblocking(False)
    print('Accepted connection from this client: ', ipAddress)
    logging.info('Accepted connection from this client: ', ipAddress)
    selector.register(connection, server_Events, data=server_Data)
    
# Method for handling incoming data
def handling_Incoming_Data (key, value):
    socket = key.fileobj
    data = value.data
    
    if value & selectors.EVENT_READ:
        # Might need to increase buffe size based on data in the future
        incoming_Data = socket.recv(1028)
        if incoming_Data:
            data.outgoing_Data += incoming_Data
        else:
            print('Closing connection to: ', data.ipAddress)
            logging.info('Closing connection to: ', data.ipAddress)
            selector.unregister(socket)
            socket.close()


#def main():
listening_Socket()

try:
    while True:
        events = selector.select(timeout=None)
        for key, value in events:
            if key.data is None:
                accept_connection(key.fileobj)
            else:
                message = key.data
                try:
                    print(message)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()
                
    
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")

finally:
    selector.close()