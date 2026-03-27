import time
from datetime import datetime
from csv import writer
import threading
from queue import Queue
import adafruit_bmp3xx
import wireless_communication_cansat as wcom_c

log = False
save_data = False
SleepTime = 1

print_lock = threading.Lock()
data_queue = Queue()

def init(i2c, address, lock):
    global bmp, i2c_lock
    i2c_lock = lock
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c, address=address)
    bmp.pressure_oversampling = 8
    bmp.temperature_oversampling = 2
    bmp.sea_level_pressure = 1013.25
    threading.Thread(target=start).start()
    if save_data:
        threading.Thread(target=SaveData).start()

def start():
    while True:
        with i2c_lock:
            t = round(bmp.temperature, 2)
            p = round(bmp.pressure, 2)
            a = round(bmp.altitude, 2)
        timestamp = datetime.now()
        data = {
            "time": timestamp,
            "temperature": t,
            "pressure": p,
            "altitude": a
        }
        result = wcom_c.send(data)
        data_queue.put(data)
        if log:
            with print_lock:
                print("[BMP390] Temperature:", f"{t}\nPressure:", f"{p}\nAltitude:", f"{a}")
                print(f"[RADIO] {result}")
        time.sleep(SleepTime)

def SaveData():
    with open('./Data/BMP390_data.csv', 'a', buffering=1, newline='') as f:
        data_writer = writer(f)
        while True:
            data = data_queue.get()
            data_writer.writerow([
                data["time"].strftime("%d-%m-%Y"),
                data["time"].strftime("%H:%M:%S"),
                data["temperature"],
                data["pressure"],
                data["altitude"]
            ])
