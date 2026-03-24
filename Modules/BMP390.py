import time
from datetime import datetime
from csv import writer
import threading
import adafruit_bmp3xx
import Cansat.wireless_communication_cansat as wcom_c

log = False
SleepTime = 1

print_lock = threading.Lock()

def init(i2c, address):
    global bmp
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c, address=address)
    bmp.pressure_oversampling = 8
    bmp.temperature_oversampling = 2
    bmp.sea_level_pressure = 1013.25
    threading.Thread(target=start, daemon=True).start()

def start():
    print("started")
    while True:
        t = round(bmp.temperature, 2)
        p = round(bmp.pressure, 2)
        a = round(bmp.altitude, 2)
        result = wcom_c.send({"temperature": t, "pressure": p, "altitude": a})
        print(f"done, {SleepTime}, {log}")
        if log:
            with print_lock:
                print("Temperature:", f"{t}\nPressure:", f"{p}\nAltitude:", f"{a}")
                print(result)
                # print("Pressure:", f"{bmp.pressure:.2f}")
                # print("Altitude:", f"{bmp.altitude:.2f}")
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
    data.append(f"{bmp.temperature:.2f}")
    data.append(f"{bmp.pressure:.2f}")
    data.append(f"{bmp.altitude:.2f}")
    return data
