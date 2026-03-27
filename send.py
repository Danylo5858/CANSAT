from sx126x import sx126x
import time

radio = sx126x("/dev/serial0", 868, 0x0001, 22, True)

def send_msg(radio, dest_addr, msg):
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

while True:
    send_msg(radio, 0x0002, b"Hola desde A")
    print("Enviado")
    time.sleep(2)
