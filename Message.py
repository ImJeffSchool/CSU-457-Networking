import sys
import selectors
import json
import struct
import io
import logging
import time
import Jeopardy

logging.basicConfig(filename='logs/Message.log', level=logging.INFO)

class Message:
    def __init__(self, selector, sock, addr, role='server', gameInstance=None):
        """
        selector: The selector object used for managing IO operations.
        sock: The socket object.
        addr: Address of the connection.
        role: Defines if the instance is being used on the 'client' or 'server' side.
        gameInstance: Optional, used to reference game state if needed (primarily on server).
        """
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.role = role
        self.request = None
        self.response = None
        self.jsonheader = None
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.gameInstance = gameInstance

    def process_read_write(self, value = None):
        if value & selectors.EVENT_READ:
            return self.read()
        if value & selectors.EVENT_WRITE:
            self.write()

    def create_message(self):
        """
        Creates a message, encoding the content and attaching headers.
        $Content: The content to send.
        Finishes by populating the self._send_buffer w/ bytestring message
        """
        if self.role == 'client': 
            content_bytes = self._json_encode(self.request['Content'], 'utf-8')
        if self.role == 'server': 
            content_bytes = self._json_encode(self.response['Content'], 'utf-8')
        
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": 'text/json',
            "content-encoding": 'utf-8',
            "content-length": len(content_bytes),
        }
        
        jsonheader_bytes = self._json_encode(jsonheader, 'utf-8')
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        self._send_buffer += message

    def handle_server_logic(self):
        if self.request == None: 
            return
        
        #response = None
        action = self.request["Action"]
        value = self.request["Value"]
        actionValue = action + ", " + value
        return actionValue

    def handle_client_logic(self):
        print("Made it to handle_client_logic\n")

    def read(self):
        """Reads incoming data from the socket and processes headers and message."""
        try:
            data = self.sock.recv(4096)
        except BlockingIOError:
            return
        
        if data:
            self._recv_buffer += data
        else:
            raise RuntimeError("Peer closed.")
        
        if self._jsonheader_len is None:
            self.process_protoheader()
        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()
        if self.jsonheader:
            return self.process_message()

        self._jsonheader_len = None
        self.jsonheader = None

    def write(self):
        """Sends the message to the socket. Use this to populate send_buffer and send to current client"""
        if self.role == 'server': 
            self.handle_server_logic()
        if self.role == 'client': 
            self.create_message()
        
        if self._send_buffer:
            print(f"Sending message to {self.addr}")
            try:
                sent = self.sock.send(self._send_buffer)
                print("Sent!!!!\n")
            except BlockingIOError:
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
            
            self.toggleReadWriteMode('r')

    def process_message(self):
        """Processes the message by reading the JSON header and content. This method can be expanded to handle server-specific or client-specific logic."""
        content_len = self.jsonheader["content-length"]
        
        if len(self._recv_buffer) >= content_len:
            data = self._recv_buffer[:content_len]
            self._recv_buffer = self._recv_buffer[content_len:]
            encoding = self.jsonheader["content-encoding"]
            
            if self.role == "server":
                self.request = self._json_decode(data, encoding)
                actionValue = self.handle_server_logic()
                return actionValue
            elif self.role == "client":
                self.response = self._json_decode(data, encoding)
                self.handle_client_logic()
    
    def process_protoheader(self):
        """Processes the protocol header to determine the length of the JSON header."""
        hdrlen = 2
        
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(">H", self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        """Processes the JSON header by reading the necessary fields."""
        hdrlen = self._jsonheader_len
        
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(self._recv_buffer[:hdrlen], "utf-8")
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(io.BytesIO(json_bytes), encoding=encoding, newline="")
        obj = json.load(tiow)
        tiow.close()
        return obj

    def toggleReadWriteMode(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r": 
            events = selectors.EVENT_READ
        elif mode == "w": 
            events = selectors.EVENT_WRITE
        elif mode == "rw":  
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else: 
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        
        self.selector.modify(self.sock, events, data=self)

    def set_client_request(self, request):
        self.request = request

    def create_server_message(self, response):
        """Sets content: response, and sets type & encoding"""
        return {
            "type": "text/json",
            "encoding": "utf-8",
            "content": response
        }

    def __repr__(self):
        return (f"Messaging Instance:\n"
                f"Role: {self.role}\n"
                f"Address: {self.addr}\n"
                f"Selector: {self.selector}\n"
                f"Socket: {self.sock}\n"
                f"Game Instance: {'Present' if self.gameInstance else 'None'}\n"
                f"Receive Buffer Size: {len(self._recv_buffer)}\n"
                f"Send Buffer Size: {len(self._send_buffer)}\n"
                f"JSON Header Length: {self._jsonheader_len}\n"
                f"JSON Header: {self.jsonheader}\n"
                f"Response: {self.response}\n"
                f"Request: {self.request}\n")