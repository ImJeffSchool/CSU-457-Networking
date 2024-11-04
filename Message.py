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
