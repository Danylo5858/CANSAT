from sx126x import sx126x
import time

radio = sx126x("/dev/serial0", 868, 0x0001, 22, True)

print("TX node A")

while True:
    msg = bytes([0x00, 0x02, radio.cfg_reg[8]]) + b"Hola desde A"
    radio.send(msg)
    print("Sent:", msg)
    time.sleep(2)
