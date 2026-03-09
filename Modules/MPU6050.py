import time
from datetime import datetime
from csv import writer
import threading
import adafruit_mpu6050

log = False
SleepTime = 1

print_lock = threading.Lock()

def init(i2c, address):
    global mpu
    mpu = adafruit_mpu6050.MPU6050(i2c, address=address)
    threading.Thread(target=start, daemon=True).start()

def start():
    while True:
        if log:
            with print_lock:
                print("Giroscopio:", mpu.gyro)
        time.sleep(SleepTime)

def SaveData(frequency):
    with open('./Data/MPU6050_data.csv', 'a', buffering=1, newline='') as f:
        data_writer = writer(f)
        while True:
            data = GetData()
            data_writer.writerow(data)
            time.sleep(frequency)

def GetData():
    data = []
    data.append(datetime.now().strftime("%d-%m-%Y"))
    data.append(datetime.now().strftime("%H:%M:%S"))
    data.append(mpu.gyro)
    return data
