import adafruit_bmp3xx
import threading
from csv import writer
from datetime import datetime
import time

log = False
SleepTime = 1

def init(i2c, address):
    global bmp
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c, address=address)
    bmp.pressure_oversampling = 8
    bmp.temperature_oversampling = 2
    bmp.sea_level_pressure = 1013.25
    threading.Thread(target=start, daemon=True).start()

def start():
    while True:
        if log:
            print("Temperature:", bmp.temperature)
            print("Pressure:", bmp.pressure)
            print("Altitude:", bmp.altitude)
        time.sleep(SleepTime)

def SaveData(frequency):
    with open('./Data/BMP390_data.csv', 'a', buffering=1, newline='') as f:
        data_writer = writer(f)
        while True:
            data = GetData()
            data_writer.writerow(data)
            time.sleep(frequency)

def GetData():
    data = []
    data.append(datetime.now().strftime("%d-%m-%Y"))
    data.append(datetime.now().strftime("%H:%M:%S"))
    data.append(bmp.temperature)
    data.append(bmp.pressure)
    data.append(bmp.altitude)
    return data
