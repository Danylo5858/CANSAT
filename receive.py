from sx126x import sx126x
import time

radio = sx126x(
    serial_num="/dev/serial0",
    freq=868,
    addr=0x0002,
    power=22,
    rssi=True
)

print("Nodo B escuchando...")

while True:
    radio.receive()
    time.sleep(0.5)
