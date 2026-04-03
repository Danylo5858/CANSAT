import struct
from sx126x import sx126x
from log_manager import log_queue

log = False

buffer = {}

def init(self_address, destination_address, frequency):
    global radio, dest_addr, freq
    dest_addr = destination_address
    freq = frequency
    radio = sx126x("/dev/serial0", freq, self_address, 22, False)

def pack_all(data):
    gps = data["GPS"]
    bmp = data["BMP390"]
    quats = data["MPU6050"]
    packet = struct.pack(
        '<iiB hhh h' + '16h',
        int(gps["latitude"] * 1e7),
        int(gps["longitude"] * 1e7),
        int(gps["satellites"]),
        int(bmp["temperature"] * 100),
        int(bmp["pressure"] * 10),
        int(bmp["altitude"] * 10),
        0,
        *[int(x * 32767) for q in quats for x in q]
    )
    return packet

def send_raw(packet):
    dest_h = (dest_addr >> 8) & 0xFF
    dest_l = dest_addr & 0xFF
    src_h = (radio.addr >> 8) & 0xFF
    src_l = radio.addr & 0xFF
    ch = radio.offset_freq
    data = bytes([
        dest_h, dest_l, ch,
        src_h, src_l, ch
    ]) + packet
    radio.send(data)

def send_data():
    packet = pack_all(buffer)
    send_raw(packet)
    if log:
        log_queue.put(f"Enviando datos: {buffer}")
    buffer.clear()
