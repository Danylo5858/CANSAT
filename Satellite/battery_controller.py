import smbus2
import time

bus = smbus2.SMBus(1)
ADDR = 0x36

def read_percent():
    data = bus.read_word_data(ADDR, 0x04)
    value = ((data & 0xFF) << 8) | (data >> 8)
    return value / 256.0

while True:
    print(f"{read_percent():.1f}%")
    time.sleep(2)
