import time
import json
from sx126x import sx126x
from log_manager import log_queue

log = False

radio = sx126x("/dev/serial0", 868, 2, 22, False)

def OnReceive(str_data):
	if log:
		log_queue.put(str_data)
	#data = json.loads(str_data)

def receiver():
	while True:
		radio.receive(OnReceive)
		time.sleep(0.5)
