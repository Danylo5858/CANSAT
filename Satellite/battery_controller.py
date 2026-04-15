import smbus2
import time

ADDR = 0x36
bus = smbus2.SMBus(1)

def read_percent():
    try:
        data = bus.read_word_data(ADDR, 0x04)

        # Swap de bytes (endianness MAX1704x)
        value = ((data & 0xFF) << 8) | (data >> 8)

        percent = value / 256.0

        # Clamp por seguridad
        return max(0, min(100, percent))

    except Exception as e:
        print("Error leyendo batería:", e)
        return None

while True:
    p = read_percent()

    if p is not None:
        print(f"Batería: {p:.1f}%")
    else:
        print("No se pudo leer batería")

    time.sleep(2)
