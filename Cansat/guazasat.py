import time
import os
import threading
import board
import busio
import RPi.GPIO as GPIO
from queue import Queue
from Modules import BMP390 as bmp
from Modules import MPU6050 as mpu
from Modules import GPS as gps

os.makedirs("Data", exist_ok=True)

log_queue = Queue()
def logger():
    while True:
        msg = log_queue.get()
        print(msg)
threading.Thread(target=logger, daemon=True).start()

i2c_lock = threading.Lock()
i2c = busio.I2C(board.SCL, board.SDA)
with i2c_lock:
    print("Devices: ", [hex(device_address) for device_address in i2c.scan()])

GlobalSleepTime = 1

bmp.save_data = True
bmp.log = log_queue
bmp.SleepTime = GlobalSleepTime
bmp.init(i2c, 0x76, i2c_lock)

mpu.save_data = True
#mpu.log = log_queue
mpu.SleepTime = GlobalSleepTime
mpu.init(i2c, 0x68, i2c_lock)

gps.save_data = True
#gps.log = log_queue
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
