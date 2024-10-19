import sys
import selectors
import json
import io
import struct
import logging
import Jeopardy
import Player

logging.basicConfig(filename='Message.log', level=logging.INFO)

class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        
    def getJson(self):
        return self.request
        
    def read(self):
        try:
            data = self.sock.recv(4096)
        except BlockingIOError:
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                logging.info('Peer closed.')
                raise RuntimeError("Peer closed.")
            
        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.processRequest()
            
    def write(self):
        if self.request:
            if not self.response_created:
                self.createResponse()
        
        if self._send_buffer:
            print("sending", repr(self._send_buffer), "to", self.addr) 
            logging.info('sending' + (repr(self._send_buffer)) + "to" + str(self.addr))
            try:
                # Should be ready to write
                dataSent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[dataSent:]
                if dataSent and not self._send_buffer:
                    self.close()
    
        
    def createResponse(self):
        print("issues here: ")
    
        
        
    def processReadWrite(self, value = None):
        if value & selectors.EVENT_READ:
            self.read()
        if value & selectors.EVENT_WRITE:
            self.write()
    
    def processRequest(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        
        encoding = self.jsonheader["content-encoding"]
        self.request = self._json_decode(data, encoding)
        print("received request", repr(self.request), "from", self.addr)
        
        
        #switch statements only available in python 3.10 and later
        #(SSH python is version 3.6)
        
        '''
        action = self.request["action"]
        
        if action == "Ready":
            print("add logic to begin game")
            
            
            
        elif action == "-h":
            print("Welcome to Jeopardy!. When you are ready to play the game please ")
        elif action == "-i":
            #hard coded for now, is a static variable in server.py
            print("The IP address of the server is: 127.0.0.1")    
        elif action == "-p":
            #also hard coded for now
            print("the listening port of the server is: 54321")
        elif action == "-n":
            #i have no idea
            print("The DNS name of the server is: ???")
        '''
            
        
    # Set selector to listen for write events, we're done reading.
        self.toggleReadWriteMode("w")
            
    def close(self):
        print("closing connection to", self.addr)
        logging.info("closing connection to "+ str(self.addr))
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )
            
            
    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj
    
    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)
    
    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')
    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]
            
            
    def toggleReadWriteMode(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        '''Was originally referred to as _set_selector_events_mask'''
        
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)