import time
from datetime import datetime
from csv import writer
import threading
from queue import Queue
import adafruit_bmp3xx
from log_manager import log_queue
from wireless_communication_cansat import msg_queue

log = False
save_data = False
send_data = False
SleepTime = 1

data_queue = Queue()

def init(i2c, address, lock):
    global bmp, i2c_lock
    i2c_lock = lock
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c, address=address)
    bmp.pressure_oversampling = 8
    bmp.temperature_oversampling = 2
    bmp.sea_level_pressure = 1013.25
    threading.Thread(target=start, daemon=True).start()
    if save_data:
        threading.Thread(target=SaveData, daemon=True).start()

def start():
    while True:
        with i2c_lock:
            t = round(bmp.temperature, 2)
            p = round(bmp.pressure, 2)
            a = round(bmp.altitude, 2)
        radio_data = {
            "temperature": t,
            "pressure": p,
            "altitude": a
        }
        if send_data:
            msg_queue.put(radio_data)
        data = radio_data
        timestamp = datetime.now()
        data["time"] = timestamp
        data_queue.put(data)
        if log:
            log_queue.put(f"Temperature: {t}\nPressure: {p}\nAltitude: {a}")
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
