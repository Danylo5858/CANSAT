from sx126x import sx126x
import time

radio = sx126x("/dev/serial0", 868, 0x0002, 22, True)

while True:
    radio.receive()
    time.sleep(0.5)
