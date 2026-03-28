import time
import json
import gzip
from queue import Queue
from sx126x import sx126x
from graph_manager import data_queue as gm_data_queue
from log_manager import log_queue

log = False

received_data = Queue()

def init(self_address, frequency):
	global radio
	radio = sx126x("/dev/serial0", frequency, self_address, 22, False)

def OnReceive(raw_data):
	str_data = gzip.decompress(raw_data).decode("utf-8")
	if log:
		log_queue.put("Datos recibidos: " + str_data)
	data = json.loads(str_data)
	received_data.put(data)

def receiver():
	while True:
		radio.receive(OnReceive)
