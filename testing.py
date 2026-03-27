import RPi.GPIO as GPIO
import time

RESET = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(RESET, GPIO.OUT)

print("FORZANDO RESET LOW (10s)...")
GPIO.output(RESET, 0)
time.sleep(10)

print("LEYENDO BUSY durante RESET:")
for i in range(10):
    print(GPIO.input(22))  # BUSY supuesto
    time.sleep(1)

GPIO.output(RESET, 1)

print("RESET LIBERADO")

for i in range(10):
    print(GPIO.input(22))
    time.sleep(1)

GPIO.cleanup()
