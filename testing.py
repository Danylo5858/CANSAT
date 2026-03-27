import RPi.GPIO as GPIO
import spidev
import time

# PINOUT CORRECTO WAVESHARE SX126X PI ZERO
BUSY = 24
RESET = 22

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(BUSY, GPIO.IN)
GPIO.setup(RESET, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.mode = 0
spi.max_speed_hz = 1000000

def wait_busy():
    while GPIO.input(BUSY) == 1:
        pass

print("RESET...")
GPIO.output(RESET, 0)
time.sleep(0.1)
GPIO.output(RESET, 1)
time.sleep(0.1)

print("BUSY inicial:", GPIO.input(BUSY))

print("\nTEST SPI GetStatus:")
resp = spi.xfer2([0xC0, 0x00])
print("GetStatus:", resp)

print("\nMONITOR BUSY:")
while True:
    print(GPIO.input(BUSY))
    time.sleep(0.5)
