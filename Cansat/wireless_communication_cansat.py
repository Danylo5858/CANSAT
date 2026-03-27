from sx126x import sx126x
from queue import Queue

radio = sx126x("/dev/serial0", 868, 0x0001, 22, True)
dest_addr = 0x0002
msg_queue = Queue()
print("WIRELEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEES INIT")

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
