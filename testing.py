import serial
import time

ports = ["/dev/serial0", "/dev/ttyS0", "/dev/ttyAMA0"]

cmd = bytes([0xC1, 0x00, 0x09])

for p in ports:
    try:
        print("\n=== Testing", p, "===")
        ser = serial.Serial(p, 9600, timeout=1)

        ser.flushInput()
        ser.write(cmd)
        time.sleep(0.5)

        data = ser.read(100)

        print("Response:", data)

        ser.close()

    except Exception as e:
        print("Error:", e)
