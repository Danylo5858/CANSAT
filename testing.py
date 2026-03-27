import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 500000

print("TEST SPI CONTINUO")

while True:
    resp = spi.xfer2([0xC0, 0x00])
    print("GetStatus:", resp)
    time.sleep(1)
