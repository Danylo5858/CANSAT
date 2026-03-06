import Modules.BMP390 as bmp
import Modules.MPU6050 as mpu
import Modules.GPS as gps
import threading
import board
import busio
import RPi.GPIO as GPIO
import time

GlobalSleepTime = 1
i2c = busio.I2C(board.SCL, board.SDA)
print("Devices: ", [hex(device_address) for device_address in i2c.scan()])

mpu.SleepTime = GlobalSleepTime
mpu.log = True
mpu.init(i2c, 0x68)

bmp.SleepTime = GlobalSleepTime
bmp.log = True
bmp.init(i2c, 0x76)

gps.SleepTime = GlobalSleepTime
gps.log = True
gps.init(i2c, 0x10)

mpu_thread = threading.Thread(target=mpu.SaveData, args=(GlobalSleepTime), daemon=True)
bmp_thread = threading.Thread(target=bmp.SaveData, args=(GlobalSleepTime), daemon=True)
gps_thread = threading.Thread(target=gps.SaveData, args=(GlobalSleepTime), daemon=True)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT) # LED
GPIO.setup(15, GPIO.OUT) # BUZZER
GPIO.output(17, GPIO.HIGH)

while True:
    GPIO.output(15, GPIO.HIGH)
    time.sleep(GlobalSleepTime)
    GPIO.output(15, GPIO.LOW)
