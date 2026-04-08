import time
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
    unpacked = struct.unpack('<iiB i i i h q 16h', packet)
    lat = unpacked[0] / 1e7
    lon = unpacked[1] / 1e7
    sats = unpacked[2]
    temp = unpacked[3] / 100
    pressure = unpacked[4] / 100
    altitude = unpacked[5] / 100
    accel_raw = unpacked[7:19]
    accel = [
        accel_raw[i:i+3]
        for i in range(0, 12, 3)
    ]
    accel = [
        [x / 100 for x in p]
        for p in accel
    ]
    duration = unpacked[19] / 1000.0
    return {
        "GPS": {
            "latitude": lat,
            "longitude": lon,
            "satellites": sats
        },
        "BMP390": {
            "temperature": temp,
            "pressure": pressure,
            "altitude": altitude
        },
        "MPU6050": {
            "time": duration,
            "accel": accel
        }
    }

def on_receive(packet):
	data = unpack_all(packet)
	received_data.put(data)
	if log:
		log_queue.put(f"Datos recibidos: {data}")

def receiver():
	while True:
		radio.receive(on_receive)
