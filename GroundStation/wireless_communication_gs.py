import time
import json
from sx126x import sx126x
from log_manager import log_queue

radio = sx126x("/dev/serial0", 868, 2, 22, False)

def OnReceive(data):
	log_queue.put(data)

def receiver():
	while True:
		radio.receive(OnReceive)
		time.sleep(0.5)
