import sys
import selectors
import json
import struct
import io
import logging
import time
import Jeopardy

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
        self.requestQueued = None
        self.responseQueued = None
        self.responseSent = None
        self.updateSent = None

    def create_message_server(self, response):
        return {
            "type": "text/json",
            "encoding": "utf-8",
            "content": response
        }
        
    def create_message(self):
        """
        Creates a message, encoding the content and attaching headers.
        $Content: The content to send.
        Finishes by populating the self._send_buffer w/ bytestring message
        """
        content_encoding = 'utf-8'
        if self.role == 'client': content_bytes = self._json_encode(self.request['content'], content_encoding)
        else: content_bytes = self._json_encode(self.response['content'], content_encoding)
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": 'text/json',
            "content-encoding": content_encoding,
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
            
            
            #*******************************
            # Handle role-specific logic
            #*******************************
            
            if self.role == "server":
                self.request = self._json_decode(data, encoding)
                print("received request", repr(self.request), "from", self.addr)
                
                #print(f"Wanting to handle server logic w/message: {repr(self)}\n")
                self.handle_server_logic()
                
            elif self.role == "client":
                self.response = self._json_decode(data, encoding)
                # Might need to move this further down the logic tree
                self.prevResponse = self.response
            
                #print(f"Wanting to handle client logic w/message: {repr(self)}\n")
                self.handle_client_logic()
            return True
        return False
            
    def handle_server_logic(self):
        """
        Server-side logic for processing responses or incoming actions.
        Example: Process actions based on game instance.
        """
        # if self.request:
        #     print(f"In handle_server_logic w/{self.request} as the client request\n")

        if self.request:
            response = None
            action = self.request["action"]
            value = self.request.get("value", None)

            # Specific player wants to ready up
            if action == 'Ready' and self.gameInstance:
                for player in self.gameInstance.playerList:
                    if player.getAddress() == self.addr: player.setReadyState(True)   
                    #print(f"{repr(player)} isReady is now {player.getReadyState()}") 
                    response = {"Action": "Ready", "Value": "You are Ready-ed Up!"}
                    #"You're Ready-ed Up!"
            elif action == "Blast":
                response = {"Action": "Blast", "Value": value}
            elif action == "Update":
                response = {"Action": "Update", "Value": value}
                self.updateSent = True
            elif action == "PlayerSelection":
                x, y = value.split(",")
                question = self.gameInstance.questionsANDanswers.currentQuestionBoard[int(x)][int(y)]
                self.gameInstance.questionsANDanswers.currentQuestionBoard[int(x)][int(y)] = "EMPTY"
                response = {"Action": "SelectedQuestion", "Value": str(question)}
                
            elif action == "PlayerAnswer":
                print("TEST PLAYER ANSWER")
            
                #can modify this text to do multiple rounds and final round
                # will change [TYPING INTO TERMINAL] 
                # to "press ready button" later 

            # Need to queue that we want to respond to the player, 
            self.responseQueued = True
            self.set_server_response(self.create_message_server(response))
            self.create_message()
            self.toggleReadWriteMode("w")
            self.request = None

        if self.responseQueued:
            self.responseQueued = False

    def handle_client_logic(self):
        """
        Client-side logic for processing responses from the server.
        Example: Handle responses from the server and act accordingly.
        """
        if self.request:
            pass
        
        request = {
                    "type": "text/json",
                    "encoding": "utf-8"
                }
        
        if self.response:
            self.request = None

            if self.response["Value"] == "You are Ready-ed Up!":
                print(self.response["Value"], "Now waiting for other players...")
                self.toggleReadWriteMode("r")
            elif self.response["Action"] == "Quit":
                #enter the logic to sock.remove() a player then 
                # msg blast to all other players who disconnected
                pass
            elif self.response["Action"] == "Blast":
                self.toggleReadWriteMode("r")
                print(self.response["Value"])
            elif self.response["Action"] == "Update":
                print(self.response["Value"]["QuestionBoard"]["CurrentBoard"])
                self.toggleReadWriteMode('r')
                #gameInstance.liveGame = self.response["Value"]
            elif self.response["Action"] == "YourTurn":
                action = "PlayerSelection"
                value = input("It is now your turn. Please select a question. (Enter like <ColNumber, RowNumber>")
                request["content"] = {"action": action, "value": value}
                self.set_client_request(request)
                self.toggleReadWriteMode("w")
                
            elif self.response["Action"] == "SelectedQuestion":
                print(self.response["Value"])
                action = "PlayerAnswer"
                value = input("Please enter your answer to the question: ")
                request['content'] = {'action': action, 'value': value}
                self.set_client_request(request)
                self.toggleReadWriteMode('w')
                
            else:
                self.toggleReadWriteMode("w")

            
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
        
        while True:
            if self._jsonheader_len is None:
                if not self.process_protoheader():
                    break

            if self._jsonheader_len is not None:
                if self.jsonheader is None:
                    if not self.process_jsonheader():
                        break
            if self.jsonheader:
                if not self.process_message():
                    break
            
            self._jsonheader_len = None
            self.jsonheader = None
        #self.toggleReadWriteMode('w')

    def write(self):
        """
        Sends the message to the socket. Use this method to write the message buffer.
        :param message: Message to be sent.
        """
        if self.role == 'server':
            # print("We want to write as the server\n")
            # print(f"Current Message OBJ is: {repr(self)}\n")
            self.handle_server_logic()
        else: 
            # print("We want to write as the client\n")
            # print(f"Current Message OBJ is: {repr(self)}\n")
            self.create_message()
            if self.request:
                self.requestQueued = True

        #Should only get here if create_message has been called be either
        if self._send_buffer:
            # print(self._recv_buffer)
            print(f"Sending message to {self.addr}\n")
            try: 
                sent = self.sock.send(self._send_buffer)
                print("Sent!!!!\n")
            except BlockingIOError:
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                if self.role == "client" and sent and not self._send_buffer:
                    #if the buffer is empty
                    #self.close()
                    self.toggleReadWriteMode("r")
        if self.requestQueued:
            if not self._send_buffer:
                self.toggleReadWriteMode("r")

        #self.toggleReadWriteMode('w')

    def process_protoheader(self):
        """
        Processes the protocol header to determine the length of the JSON header.
        """
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(">H", self._recv_buffer[:hdrlen])[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]
            return True
        return False

    def process_jsonheader(self):
        """
        Processes the JSON header by reading the necessary fields.
        """
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(self._recv_buffer[:hdrlen], "utf-8")
            self._recv_buffer = self._recv_buffer[hdrlen:]
            return True
        return False

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
           # print("Client mode is now set to: r\n")            
            events = selectors.EVENT_READ
        elif mode == "w":
            # print("Client mode is now set to: w\n")
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            # print("Client mode is now set to: r/w\n")
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def set_client_request(self, request):
        self.request = request
        
    def set_server_request(self, request):
        self.request = request

    def set_server_response(self, response):
        self.response = response

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
                f"PrevResponse: {self.prevResponse}\n")