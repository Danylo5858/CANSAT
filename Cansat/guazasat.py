import time
import os
import threading
import board
import busio
import RPi.GPIO as GPIO
from Modules import BMP390 as bmp
from Modules import MPU6050 as mpu
from Modules import GPS as gps

GlobalSleepTime = 1

i2c_lock = threading.Lock()

i2c = busio.I2C(board.SCL, board.SDA)
ẃith i2c_lock:
    print("Devices: ", [hex(device_address) for device_address in i2c.scan()])

os.makedirs("Data", exist_ok=True)

bmp.log = True
bmp.save_data = True
bmp.SleepTime = GlobalSleepTime
bmp.init(i2c, 0x76, i2c_lock)

mpu.log = True
mpu.save_data = True
mpu.SleepTime = GlobalSleepTime
mpu.init(i2c, 0x68, i2c_lock)

gps.log = True
gps.save_data = True
gps.SleepTime = GlobalSleepTime
gps.init(i2c, 0x10, i2c_lock)

#threading.Thread(target=mpu.SaveData, args=(GlobalSleepTime,), daemon=True).start()
#threading.Thread(target=bmp.SaveData, args=(GlobalSleepTime,), daemon=True).start()
#threading.Thread(target=gps.SaveData, args=(GlobalSleepTime,), daemon=True).start()

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT) # LED
GPIO.setup(15, GPIO.OUT) # BUZZER
GPIO.output(17, GPIO.HIGH)

while True:
    GPIO.output(15, GPIO.HIGH)
    time.sleep(GlobalSleepTime)
    GPIO.output(15, GPIO.LOW)
