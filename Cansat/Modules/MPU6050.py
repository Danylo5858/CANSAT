import time
from datetime import datetime
from csv import writer
import threading
from queue import Queue
import adafruit_mpu6050

log = None
save_data = False
SleepTime = 1

data_queue = Queue()

def init(i2c, address, lock):
    global mpu, i2c_lock
    i2c_lock = lock
    mpu = adafruit_mpu6050.MPU6050(i2c, address=address)
    threading.Thread(target=start, daemon=True).start()
    if save_data:
        threading.Thread(target=SaveData, daemon=True).start()

def start():
    while True:
        with i2c_lock:
            gyro = mpu.gyro
        timestamp = datetime.now()
        data = {
            "time": timestamp,
            "gyro": gyro
        }
        data_queue.put(data)
        if log is not None:
            log.put(f"Giroscopio: {gyro}")
        time.sleep(SleepTime)

def SaveData():
    with open('./Data/MPU6050_data.csv', 'a', buffering=1, newline='') as f:
        data_writer = writer(f)
        while True:
            data = data_queue.get()
            data_writer.writerow([
                data["time"].strftime("%d-%m-%Y"),
                data["time"].strftime("%H:%M:%S"),
                data["gyro"]
            ])
