import time
import json
from queue import Queue, Empty
from sx126x import sx126x

freq = 868
dest_addr = 2
radio = sx126x("/dev/serial0", freq, 1, 22, False)

msg_queue = Queue()
buffer = []
interval = 1.0

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

def sender():
    while True:
        start = time.time()
        while (time.time() - start) < interval:
            try:
                msg = msg_queue.get(timeout=interval-(time.time()-start))
                buffer.append(msg)
            except Empty:
                break
        if buffer:
            send(json.dumps(buffer, default=str))
            buffer.clear()
