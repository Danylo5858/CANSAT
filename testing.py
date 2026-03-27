import RPi.GPIO as GPIO
import time

M0 = 22
M1 = 27

GPIO.setmode(GPIO.BCM)
GPIO.setup(M0, GPIO.OUT)
GPIO.setup(M1, GPIO.OUT)

print("Modo normal")
GPIO.output(M0, 0)
GPIO.output(M1, 0)
time.sleep(2)

print("Modo config")
GPIO.output(M0, 0)
GPIO.output(M1, 1)
time.sleep(2)

print("Modo sleep/config test terminado")
GPIO.cleanup()
