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
        
    def createMessage(self):
        message1 = input("Enter a message you would like to send to the server: ")
        message1 = message1.encode()
        #messages = [message1, message2]
        self._send_buffer += message1
        
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
        self.close()
 
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