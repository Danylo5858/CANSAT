import struct
from sx126x import sx126x
from battery_controller import read_percent
from log_manager import log_queue

log = False

buffer = {}

def init(self_address, destination_address, frequency):
    global radio, dest_addr, freq
    dest_addr = destination_address
    freq = frequency
    radio = sx126x("/dev/serial0", freq, self_address, 22, False)

def pack_all(data):
    print(int(read_percent()))
    gps = data["GPS"]
    bmp = data["BMP390"]
    accel_points = data["MPU6050"]["accel"]
    duration = data["MPU6050"]["time"]
    packet = struct.pack(
        '<iiB i i i h' + '12h' + 'I',
        int(gps["latitude"] * 1e7),
        int(gps["longitude"] * 1e7),
        int(gps["satellites"]),
        # int(read_percent()),
        int(bmp["temperature"] * 100),
        int(bmp["pressure"] * 100),
        int(bmp["altitude"] * 100),
        0,
        *[
            int(x * 100)
            for p in accel_points
            for x in p
        ],
        int(duration * 1000)
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
