import sys
import selectors
import json
import io
import struct
import logging

logging.basicConfig(filename='Message.log', level=logging.INFO)

class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
    
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
        
    def processReadWrite(self, value):
        if value & selectors.EVENT_READ:
            self.read()
        if value & selectors.EVENT_WRITE:
            self.write()