import time
import json
import gzip
from queue import Queue
from sx126x import sx126x
from log_manager import log_queue

log = False

received_data = Queue()

def init(self_address, frequency):
	global radio
	radio = sx126x("/dev/serial0", frequency, self_address, 22, False)

#def on_receive(raw_data):
#	str_data = gzip.decompress(raw_data).decode("utf-8")
#	if log:
#		log_queue.put("Datos recibidos: " + str_data)
#	data = json.loads(str_data)
#	received_data.put(data)

def on_receive(packet_bytes):
	decompressed = gzip.decompress(packet_bytes)
	sep = decompressed.find(b"|||")
	if sep == -1:
		raise ValueError("Separator ||| not found")
	json_part = decompressed[:sep]
	bin_part = decompressed[sep + 3:]
	str_clean = json_part.decode("utf-8")
	data = json.loads(str_clean)
	data["MPU6050_BIN"] = bin_part
	if log:
		if bin_part != None:
			log_queue.put(f"Datos recibidos: {str_clean} + MPU6050_BIN")
		else:
			log_queue.put(f"Datos recibidos: {str_clean}")
	received_data.put(data)

def receiver():
	while True:
		radio.receive(on_receive)
