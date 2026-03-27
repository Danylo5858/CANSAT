import RPi.GPIO as GPIO
import time

# Pines (modo BCM)
BUSY = 24
RESET = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(BUSY, GPIO.IN)
GPIO.setup(RESET, GPIO.OUT)

def read_busy(label=""):
    state = GPIO.input(BUSY)
    print(f"{label} BUSY = {state}")
    return state

try:
    print("=== TEST SX1262 BUSY ===\n")

    # 1. Leer estado inicial
    read_busy("Inicial")

    time.sleep(1)

    # 2. Reset del módulo
    print("\nHaciendo RESET...")
    GPIO.output(RESET, 0)
    time.sleep(0.1)
    GPIO.output(RESET, 1)

    # 3. Leer BUSY varias veces después del reset
    print("\nLeyendo BUSY después del reset:")
    for i in range(10):
        read_busy(f"t={i}")
        time.sleep(0.2)

    print("\nTest continuo (Ctrl+C para salir):")

    # 4. Monitor continuo
    while True:
        read_busy()
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nSaliendo...")

finally:
    GPIO.cleanup()
