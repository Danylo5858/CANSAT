from sx126x import sx126x
import time

print("Inicializando módulo...")

device = sx126x(
    serial_num="/dev/serial0",
    freq=868,
    addr=0x0001,
    power=22,
    rssi=True
)

print("Configurado correctamente")

while True:
    device.receive()
    time.sleep(1)
