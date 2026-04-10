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
import camera_controller as cam

GlobalSleepTime = 1

os.makedirs("Data", exist_ok=True)
os.makedirs("Pictures", exist_ok=True)

i2c_lock = threading.Lock()
i2c = busio.I2C(board.SCL, board.SDA)
with i2c_lock:
    print("Devices: ", [hex(device_address) for device_address in i2c.scan()])

logger_thread = threading.Thread(target=lm.logger, daemon=True)
logger_thread.start()

cam.log = True
cam.SleepTime = 4
cam.init((512, 512))
image_capture = threading.Thread(target=cam.capture, daemon=True)
image_capture.start()

wcom_c.log = True
wcom_c.init(1, 2, 868)

bmp.log = False
bmp.send_data = True
bmp.save_data = True
bmp.init(i2c, 0x76, i2c_lock)

mpu.log = False
mpu.send_data = True
mpu.save_data = True
mpu.init(i2c, 0x68, i2c_lock)

gps.log = False
gps.send_data = True
gps.save_data = True
gps.init(i2c, 0x10, i2c_lock)

try:
    while True:
        start = time.time()
        threads = [
            threading.Thread(target=bmp.GetData, daemon=True),
            threading.Thread(target=mpu.GetData, daemon=True), # update_motion_state => 1 sec
            threading.Thread(target=gps.GetData, daemon=True)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        wcom_c.send_data() # send => 0.3 sec
        #time.sleep(GlobalSleepTime)
        lm.log_queue.put(time.time() - start)
except KeyboardInterrupt:
    print("\nCerrando todos los procesos...")

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(17, GPIO.OUT)    # LED
#GPIO.setup(15, GPIO.OUT)    # BUZZER
#GPIO.output(17, GPIO.HIGH)

#while True:
#    GPIO.output(15, GPIO.HIGH)
#    time.sleep(GlobalSleepTime)
#    GPIO.output(15, GPIO.LOW)
