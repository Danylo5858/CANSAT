import RPi.GPIO as GPIO
import spidev
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# GPIOs candidatos típicos (HAT Waveshare + variantes)
CANDIDATE_BUSY = [24, 22, 23, 5, 6, 12, 13, 16, 17, 18, 19, 20, 21, 25]
RESET = 25  # típico Waveshare

# SPI configs a probar
SPI_CONFIGS = [(0,0), (0,1)]

GPIO.setup(RESET, GPIO.OUT)

def test_reset():
    print("\n[RESET TEST]")
    GPIO.output(RESET, 0)
    time.sleep(0.2)
    GPIO.output(RESET, 1)
    time.sleep(0.5)
    print("RESET pulsed")

def scan_busy():
    print("\n[BUSY SCAN]")
    for p in CANDIDATE_BUSY:
        GPIO.setup(p, GPIO.IN)

    for i in range(5):
        states = {p: GPIO.input(p) for p in CANDIDATE_BUSY}
        print("scan", i, states)
        time.sleep(0.5)

def test_spi(bus, dev):
    print(f"\n[SPI TEST] bus={bus} dev={dev}")

    spi = spidev.SpiDev()
    spi.open(bus, dev)
    spi.mode = 0
    spi.max_speed_hz = 1000000

    # GetStatus SX1262
    try:
        resp = spi.xfer2([0xC0, 0x00])
        print("GetStatus:", resp)
    except Exception as e:
        print("SPI error:", e)

    spi.close()

def full_run():
    print("=== SX1262 FULL DIAGNOSIS START ===")

    # 1. RESET
    test_reset()

    # 2. BUSY scan
    scan_busy()

    # 3. SPI tests
    for bus, dev in SPI_CONFIGS:
        test_spi(bus, dev)

    print("\n=== DONE ===")

try:
    full_run()

finally:
    GPIO.cleanup()
