from Modules import BMP390 as bmp
from Modules import MPU6050 as mpu
from Modules import GPS as gps
from GroundStation import graph_manager as gm
import threading
import board
import busio
import RPi.GPIO as GPIO
import time
import os

GlobalSleepTime = 1
i2c = busio.I2C(board.SCL, board.SDA)
print("Devices: ", [hex(device_address) for device_address in i2c.scan()])

os.makedirs("Data", exist_ok=True)

mpu.SleepTime = GlobalSleepTime
mpu.log = True
mpu.init(i2c, 0x68)

bmp.SleepTime = GlobalSleepTime
bmp.log = True
bmp.init(i2c, 0x76)

gps.SleepTime = GlobalSleepTime
gps.log = True
gps.init(i2c, 0x10)

threading.Thread(target=mpu.SaveData, args=(GlobalSleepTime,), daemon=True).start()
threading.Thread(target=bmp.SaveData, args=(GlobalSleepTime,), daemon=True).start()
threading.Thread(target=gps.SaveData, args=(GlobalSleepTime,), daemon=True).start()

gm.SleepTime = 10
threading.Thread(target=gm.start, daemon=True).start()

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT) # LED
GPIO.setup(15, GPIO.OUT) # BUZZER
GPIO.output(17, GPIO.HIGH)

while True:
    GPIO.output(15, GPIO.HIGH)
    time.sleep(GlobalSleepTime)
    GPIO.output(15, GPIO.LOW)
