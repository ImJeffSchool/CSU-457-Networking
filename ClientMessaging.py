import sys
import selectors
import json
import io
import struct
import logging

logging.basicConfig(filename='Message.log', level=logging.INFO)

class Message:
    def __init__(self, selector, sock, addr, request):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self.request = request
        self.requestQueued = False
        self._jsonheader_len = None
        self.jsonheader = None
        self.response = None
        
    def createRequest(self, *, contentBytes, contentType, contentEncoding):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": contentType,
            "content-encoding": contentEncoding,
            "content-length": len(contentBytes),
        }
        jsonheader_bytes = self.jsonEncode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + contentBytes
        return message
    
    
    
    def processResponse(self):
        #just here as a placeholder for now, will have to call 
        #self.close() when game is over. (In the homework this is
        # different. Close is called on the process response because
        #once a number has been doubled, negated, etc: connection
        #will close)
        self.close()
    
    def queue_request(self):
        content = self.request["content"]
        contentType = self.request["type"]
        contentEncoding = self.request["encoding"]
        req = {
            "contentBytes": self.jsonEncode(content, contentEncoding),
            "contentType": contentType,
            "contentEncoding": contentEncoding,
        }
        
        message = self.createRequest(**req)
        self._send_buffer += message
        self.requestQueued = True
        
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
    
        
    def jsonEncode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)
        
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
 
    def write(self):
        self.queue_request()
        
        
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
        
        if self.requestQueued:
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
                self.toggleReadWriteMode("r")
      
    def processReadWrite(self, value):
        if value & selectors.EVENT_READ:
            self.read()
        if value & selectors.EVENT_WRITE:
            self.write()
            
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