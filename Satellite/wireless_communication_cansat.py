from sx126x import sx126x
from queue import Queue

freq = 868
dest_addr = 2
radio = sx126x("/dev/serial0", freq, 1, 22, False)
msg_queue = Queue()

def send(str_msg):
    msg = str_msg.encode("utf-8")
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
        msg = msg_queue.get()
        send(msg)
        print(msg)
        #radio.send(b"2,868,"+msg.encode("utf-8"))
