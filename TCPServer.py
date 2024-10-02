import sys
import socket
import selectors
import types

# TCP Server code for the project

HOST = '127.0.0.1' # The server's hostname or IP address to listen on all interfaces
PORT = 60000     # The port used by the server