import time
# import json
# import gzip
import struct
from queue import Queue
from sx126x import sx126x
from log_manager import log_queue

log = False

received_data = Queue()

def init(self_address, frequency):
	global radio
	radio = sx126x("/dev/serial0", frequency, self_address, 22, False)

def unpack_all(packet):
    unpacked = struct.unpack('<iiB hhh h 16h', packet)
    lat = unpacked[0] / 1e7
    lon = unpacked[1] / 1e7
    sats = unpacked[2]
    temp = unpacked[3] / 100
    pressure = unpacked[4] / 10
    altitude = unpacked[5] / 10
    quats_raw = unpacked[7:]
    quats = [quats_raw[i:i+4] for i in range(0, 16, 4)]
    quats = [[x / 32767 for x in q] for q in quats]
    return {
        "GPS": {"latitude": lat, "longitude": lon, "satellites": sats},
        "BMP390": {"temperature": temp, "pressure": pressure, "altitude": altitude},
        "MPU6050": quats
    }

def on_receive(packet):
	data = unpack_all(packet)
	received_data.put(data)
	if log:
		log_queue.put(f"Datos recibidos: {data}")

# def on_receive(raw_data):
# 	str_data = gzip.decompress(raw_data).decode("utf-8")
# 	if log:
# 		log_queue.put("Datos recibidos: " + str_data)
# 	data = json.loads(str_data)
# 	received_data.put(data)

# def on_receive(packet_bytes):
# 	decompressed = gzip.decompress(packet_bytes)
# 	sep = decompressed.find(b"|||")
# 	if sep == -1:
# 		raise ValueError("Separator ||| not found")
# 	json_part = decompressed[:sep]
# 	bin_part = decompressed[sep + 3:]
# 	str_clean = json_part.decode("utf-8")
# 	data = json.loads(str_clean)
# 	data["MPU6050_BIN"] = bin_part
# 	if log:
# 		if bin_part != bytearray(): # bin != bytearray() NO FUNCIONA, siempre da True
# 			log_queue.put(f"Datos recibidos: {str_clean} + MPU6050_BIN")
# 		else:
# 			log_queue.put(f"Datos recibidos: {str_clean}")
# 	received_data.put(data)

def receiver():
	while True:
		radio.receive(on_receive)
