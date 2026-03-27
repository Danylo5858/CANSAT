import serial
import time

ser = serial.Serial("/dev/serial0", 9600, timeout=1)

print("Probando UART...")

ser.write(bytes([0xC1, 0x00, 0x09]))  # get config
time.sleep(0.5)

data = ser.read(ser.in_waiting or 1)

print("Respuesta:", data)
