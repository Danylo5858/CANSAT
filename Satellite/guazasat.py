import os
import time
import threading
import board
import busio
import RPi.GPIO as GPIO
from Modules import BMP390 as bmp
from Modules import MPU6050 as mpu
from Modules import GPS as gps
import log_manager as lm
import wireless_communication_cansat as wcom_c

os.makedirs("Data", exist_ok=True)

i2c_lock = threading.Lock()
i2c = busio.I2C(board.SCL, board.SDA)
with i2c_lock:
    print("Devices: ", [hex(device_address) for device_address in i2c.scan()])

threading.Thread(target=lm.logger, daemon=True).start()

GlobalSleepTime = 1

bmp.log = True
bmp.send_data = True
bmp.save_data = True
bmp.init(i2c, 0x76, i2c_lock)

mpu.log = True
mpu.send_data = True
mpu.save_data = True
mpu.init(i2c, 0x68, i2c_lock)

gps.log = True
gps.send_data = True
gps.save_data = True
gps.init(i2c, 0x10, i2c_lock)

threads = [
    threading.Thread(target=bmp.GetData, daemon=True),
    threading.Thread(target=mpu.GetData, daemon=True),
    threading.Thread(target=gps.GetData, daemon=True)
]

while True:
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    time.sleep(GlobalSleepTime)
    wcom_c.SendData()

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(17, GPIO.OUT)    # LED
#GPIO.setup(15, GPIO.OUT)    # BUZZER
#GPIO.output(17, GPIO.HIGH)

#while True:
#    GPIO.output(15, GPIO.HIGH)
#    time.sleep(GlobalSleepTime)
#    GPIO.output(15, GPIO.LOW)
