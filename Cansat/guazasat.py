import time
import os
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

threading.Thread(target=wcom_c.sender, daemon=True).start()
threading.Thread(target=lm.logger, daemon=True).start()

i2c_lock = threading.Lock()
i2c = busio.I2C(board.SCL, board.SDA)
with i2c_lock:
    print("Devices: ", [hex(device_address) for device_address in i2c.scan()])

GlobalSleepTime = 1

bmp.log = True
bmp.send_data = True
bmp.save_data = True
bmp.SleepTime = GlobalSleepTime
bmp.init(i2c, 0x76, i2c_lock)

mpu.log = False
mpu.send_data = False
mpu.save_data = True
mpu.SleepTime = GlobalSleepTime
mpu.init(i2c, 0x68, i2c_lock)

gps.log = False
gps.send_data = False
gps.save_data = True
gps.SleepTime = GlobalSleepTime
gps.init(i2c, 0x10, i2c_lock)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)    # LED
GPIO.setup(15, GPIO.OUT)    # BUZZER
GPIO.output(17, GPIO.HIGH)

while True:
    GPIO.output(15, GPIO.HIGH)
    time.sleep(GlobalSleepTime)
    GPIO.output(15, GPIO.LOW)
