import RPi.GPIO as GPIO
import spidev
import time

BUSY = 24
RESET = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(BUSY, GPIO.IN)
GPIO.setup(RESET, GPIO.OUT)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

while True:
    resp = spi.xfer2([0xC0, 0x00])
    print(resp)
    time.sleep(0.5)

def wait_busy():
    while GPIO.input(BUSY) == 1:
        pass

def write_cmd(cmd, data=[]):
    wait_busy()
    spi.xfer2([cmd] + data)
    # aquí el chip debería ponerse BUSY
    print("Después de comando, BUSY =", GPIO.input(BUSY))
    wait_busy()

try:
    print("RESET...")
    GPIO.output(RESET, 0)
    time.sleep(0.1)
    GPIO.output(RESET, 1)
    time.sleep(0.1)

    print("BUSY inicial:", GPIO.input(BUSY))

    # comando standby
    print("\nEnviando SetStandby...")
    write_cmd(0x80, [0x00])

    print("\nEnviando GetStatus...")
    resp = spi.xfer2([0xC0, 0x00])
    print("Respuesta:", resp)

    print("\nLectura continua BUSY:")
    while True:
        print("BUSY =", GPIO.input(BUSY))
        time.sleep(0.5)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()
    spi.close()
