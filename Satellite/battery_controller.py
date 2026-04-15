import smbus2

ADDR = 0x36
bus = smbus2.SMBus(1)

def read_percent():
    try:
        data = bus.read_word_data(ADDR, 0x04)
        value = ((data & 0xFF) << 8) | (data >> 8)
        percent = value / 256.0
        return max(0, min(100, percent))
    except Exception as e:
        print("Error leyendo bateria:", e)
        return None
