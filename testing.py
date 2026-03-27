import serial
import time

ports = ["/dev/serial0", "/dev/ttyS0", "/dev/ttyAMA0"]

for p in ports:
    try:
        print("\nTesting", p)
        ser = serial.Serial(p, 9600, timeout=1)
        ser.write(b'\xC1\x00\x09')
        time.sleep(0.5)
        data = ser.read(100)
        print("Response:", data)
        ser.close()
    except Exception as e:
        print("Fail:", p, e)
