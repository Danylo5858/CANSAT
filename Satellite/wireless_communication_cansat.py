import json
from sx126x import sx126x

buffer = []

def init(self_address, destination_address, frequency):
    global radio, dest_addr, freq
    dest_addr = destination_address
    freq = frequency
    radio = sx126x("/dev/serial0", freq, self_address, 22, False)

def send(str_msg):
    msg = str_msg.encode("utf-8")+b"}"
    dest_h = (dest_addr >> 8) & 0xFF
    dest_l = dest_addr & 0xFF
    src_h = (radio.addr >> 8) & 0xFF
    src_l = radio.addr & 0xFF
    ch = radio.offset_freq
    data = bytes([
        dest_h, dest_l, ch,
        src_h, src_l, ch
    ]) + msg
    radio.send(data)

def SendData():
    send(json.dumps(buffer))
    buffer.clear()
