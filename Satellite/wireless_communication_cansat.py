import json
import struct
import gzip
from sx126x import sx126x
from log_manager import log_queue

log = False

buffer = {}

def init(self_address, destination_address, frequency):
    global radio, dest_addr, freq
    dest_addr = destination_address
    freq = frequency
    radio = sx126x("/dev/serial0", freq, self_address, 22, False)

def send_raw(data):
    dest_h = (dest_addr >> 8) & 0xFF
    dest_l = dest_addr & 0xFF
    src_h = (radio.addr >> 8) & 0xFF
    src_l = radio.addr & 0xFF
    ch = radio.offset_freq
    packet = bytes([
        dest_h, dest_l, ch,
        src_h, src_l, ch
    ]) + data
    radio.send(packet)

def SendData():
   str_data = json.dumps(buffer)
   compressed = gzip.compress(str_data.encode("utf-8"))
   send_raw(compressed)
   buffer.clear()
   if log:
       log_queue.put("Enviando datos: " + str_data)

# def SendData():
#     binary = buffer.get("MPU6050_BIN", b"")
#     clean = { k:v for k,v in buffer.items() if k != "MPU6050_BIN" }
#     str_clean = json.dumps(clean)
#     json_part = str_clean.encode("utf-8")
#     size = struct.pack("<I", len(binary))
#     payload = json_part + b"|||" + size + binary
#     compressed = gzip.compress(payload)
#     send_raw(compressed)
#     buffer.clear()
#     if log:
#         if binary != b"":
#             log_queue.put(f"Datos enviados: {str_clean} + MPU6050_BIN")
#         else:
#             log_queue.put(f"Datos enviados: {str_clean}")
