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
    unpacked = struct.unpack('<iiBB i i i h 12h I', packet)
    lat = unpacked[0] / 1e7
    lon = unpacked[1] / 1e7
    sats = unpacked[2]
    battery = unpacked[3]
    temp = unpacked[4] / 100
    pressure = unpacked[5] / 100
    altitude = unpacked[6] / 100
    accel_raw = unpacked[8:20]
    accel = [
        accel_raw[i:i+3]
        for i in range(0, 12, 3)
    ]
    accel = [
        [x / 100 for x in p]
        for p in accel
    ]
    duration = unpacked[20] / 1000.0
    return {
        "BMP390": {
            "temperature": temp,
            "pressure": pressure,
            "altitude": altitude
        },
        "MPU6050": {
            "time": duration,
            "accel": accel
        },
        "GPS": {
            "latitude": lat,
            "longitude": lon,
            "satellites": sats
        },
        "battery": battery
    }

def on_receive(packet):
	data = unpack_all(packet)
	received_data.put(data)
	if log:
		log_queue.put(f"Datos recibidos: {data}")

def receiver():
	while True:
		radio.receive(on_receive)
