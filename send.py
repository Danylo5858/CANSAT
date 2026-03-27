from sx126x import sx126x
import time

radio = sx126x(
    serial_num="/dev/serial0",
    freq=868,
    addr=0x0001,
    power=22,
    rssi=True
)

print("Nodo A transmitiendo...")

while True:
    radio.send(b"Hola desde A")
    print("Enviado")
    time.sleep(2)
