import adafruit_mpu6050
from csv import writer
from datetime import datetime
import time

log = False
SleepTime = 1

def init(i2c, address):
    global mpu
    mpu = adafruit_mpu6050.MPU6050(i2c, address=address)
    start()

def start():
    while True:
        if log:
            print("Giroscopio:", mpu.gyro)
        time.sleep(SleepTime)

def SaveData(frequency):
    with open('../Data/MPU6050_data.csv', 'a', buffering=1, newline='') as f:
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
