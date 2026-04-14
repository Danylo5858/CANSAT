from datetime import datetime
from csv import writer
import threading
from queue import Queue
import adafruit_bmp3xx
from log_manager import log_queue
from wireless_communication_cansat import buffer

log = False
send_data = False
save_data = False

data_queue = Queue()

def init(i2c, address, lock):
    global bmp, i2c_lock
    i2c_lock = lock
    bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c, address=address)
    bmp.pressure_oversampling = 8
    bmp.temperature_oversampling = 2
    bmp.sea_level_pressure = 1013.25
    if save_data:
        threading.Thread(target=SaveData, daemon=True).start()

def GetData():
    with i2c_lock:
        t = round(bmp.temperature, 2)
        p = round(bmp.pressure, 2)
        a = round(bmp.altitude, 2)
    if log:
        log_queue.put(f"Temperatura: {t}\nPresion: {p}\nAltitud: {a}")
    if send_data:
        buffer["BMP390"] = {
            "temperature": t,
            "pressure": p,
            "altitude": a
        }
        #buffer.append([t, p, a])
    data = {
        "time": datetime.now(),
        "temperature": t,
        "pressure": p,
        "altitude": a
    }
    data_queue.put(data)

def SaveData():
    log_queue.put("SAVE_DATA")
    with open('./Data/BMP390_data.csv', 'a', buffering=1, newline='') as f:
        print("WITH_OPEN")
        data_writer = writer(f)
        while True:
            data = data_queue.get()
            log_queue.put("WRITING ROW...")
            data_writer.writerow([
                data["time"].strftime("%Y-%m-%d"),
                data["time"].strftime("%H:%M:%S"),
                data["temperature"],
                data["pressure"],
                data["altitude"]
            ])
