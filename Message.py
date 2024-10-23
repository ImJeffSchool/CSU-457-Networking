import sys
import selectors
import json
import struct
import io
import logging
import time

logging.basicConfig(filename='Message.log', level=logging.INFO)

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
        self.role = role  # 'client' or 'server'
        self.request = None
        self.response = None
        self.prevResponse = None
        self.jsonheader = None
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.gameInstance = gameInstance  # Relevant for server-side operations

    def create_message(self):
        """
        Creates a message, encoding the content and attaching headers.
        $Content: The content to send.
        Finishes by populating the self._send_buffer w/ bytestring message
        """
        content_encoding = 'utf-8'
        content_bytes = self._json_encode(self.request['content'], content_encoding)
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": 'text/json',
            "content-encoding": 'content_encoding',
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, content_encoding)
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        self._send_buffer += message

    def process_message(self):
        """
        Processes the message by reading the JSON header and content.
        This method can be expanded to handle server-specific or client-specific logic.
        """
        content_len = self.jsonheader["content-length"]
        if len(self._recv_buffer) >= content_len:
            data = self._recv_buffer[:content_len]
            self._recv_buffer = self._recv_buffer[content_len:]

            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            print(f"Recieved request {self.request} from {self.addr} in Message.process_message()\n")

            # Handle role-specific logic
            if self.role == 'server':
                print(f"Wanting to handle client logic w/message: {repr(self)}\n")
                self.handle_server_logic()
            elif self.role == 'client':
                print(f"Wanting to handle client logic w/message: {repr(self)}\n")
                self.handle_client_logic()

    def handle_server_logic(self):
        """
        Server-side logic for processing responses or incoming actions.
        Example: Process actions based on game instance.
        """
        print(f"In handle_server_logic w/{self.request} as the client request\n")

        if self.request:
            action = self.response.get("action")
            value = self.response.get("value")
            # Example: Handle game-specific actions
            if action == "playerAction" and self.gameInstance:
                self.gameInstance.processPlayerAction(value)
            # Add other server-specific logic as needed

    def handle_client_logic(self):
        """
        Client-side logic for processing responses from the server.
        Example: Handle responses from the server and act accordingly.
        """
        if self.response:
            # Handle client-side specific actions here
            print(f"Client received: {self.response}\n")

    def process_read_write(self, value = None):
        if value & selectors.EVENT_READ:
            self.read()
        if value & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        """
        Reads incoming data from the socket and processes headers and message.
        """
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
            self.process_message()

        self.toggleReadWriteMode('w')

    def write(self):
        """
        Sends the message to the socket. Use this method to write the message buffer.
        :param message: Message to be sent.
        """
        if self.role == 'server':
            print("We want to write as the server\n")
            print(f"Current Message OBJ is: {repr(self)}\n")
            self.handle_server_logic()
        else: 
            print("We want to write as the client\n")
            print(f"Current Message OBJ is: {repr(self)}\n")
            self.create_message()

        #Should only get here if create_message has been called be either
        if self._send_buffer:
            print(f"Sending message to {self.addr}\n")
            time.sleep(1)
            try: 
                sent = self.sock.send(self._send_buffer)
                print("Sent!!!!\n")
                time.sleep(1)
            except BlockingIOError:
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

        self.toggleReadWriteMode('r')

    def process_protoheader(self):
        """
        Processes the protocol header to determine the length of the JSON header.
        """
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(">H", self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        """
        Processes the JSON header by reading the necessary fields.
        """
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
        '''Was originally referred to as _set_selector_events_mask'''
        if mode == "r":
            print("Client mode is now set to: r\n")            
            events = selectors.EVENT_READ
        elif mode == "w":
            print("Client mode is now set to: w\n")
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            print("Client mode is now set to: r/w\n")
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def set_client_request(self, request):
        self.request = request

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
                f"Request: {self.request}\n"
                f"PreResponse: {self.prevResponse}\n")