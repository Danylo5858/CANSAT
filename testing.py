import spidev
import RPi.GPIO as GPIO
import time

# Pines (AJUSTA según tu wiring real)
RESET_PIN = 22
BUSY_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
spi.mode = 0

# -------------------------
# RESET del chip
# -------------------------
def reset_chip():
    GPIO.output(RESET_PIN, GPIO.LOW)
    time.sleep(0.01)
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(0.1)

# -------------------------
# Esperar BUSY libre
# -------------------------
def wait_busy():
    while GPIO.input(BUSY_PIN) == 1:
        time.sleep(0.001)

# -------------------------
# Enviar comando SX126x
# -------------------------
def sx_write(cmd):
    wait_busy()
    spi.xfer2(cmd)
    wait_busy()

# -------------------------
# Leer respuesta simple
# -------------------------
def sx_read(cmd, length=2):
    wait_busy()
    spi.xfer2(cmd)
    wait_busy()
    return spi.xfer2([0x00]*length)

# -------------------------
# TEST
# -------------------------
print("Resetting SX126X...")
reset_chip()

print("Probando comunicación...")

# GetStatus = 0xC0
resp = sx_read([0xC0, 0x00], 2)

print("STATUS:", resp)

# GetDeviceErrors = 0xC3
resp2 = sx_read([0xC3, 0x00, 0x00], 3)

print("ERRORS:", resp2)

spi.close()
GPIO.cleanup()
