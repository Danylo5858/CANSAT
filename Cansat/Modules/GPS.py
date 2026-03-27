import time
from datetime import datetime
from csv import writer
import threading
from queue import Queue
import adafruit_gps

log = False
dave_data = False
SleepTime = 1

print_lock = threading.Lock()
data_queue = Queue()

def init(i2c, address, lock):
    global gps, i2c_lock
    i2c_lock = lock
    gps = adafruit_gps.GPS_GtopI2C(i2c, address=address)
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    gps.send_command(b"PMTK220,1000")
    threading.Thread(target=start).start()
    if save_data:
        threading.Thread(target=SaveData).start()

def start():
    while True:
        gps.update()
        if gps.has_fix:
            with i2c_lock:
                lan = gps.latitude
                lon = gps.longitude
                sat = gps.satellites
            timestamp = datetime.now()
            data = {
                "time": timestamp,
                "latitude": lan,
                "longitude": lon,
                "satellites": sat
            }
            data_queue.put(data)
            if log:
                with print_lock:
                    print("Lat:", f"{lan:.4f}")
                    print("Lon:", f"{lon:.4f}")
                    print("Satelites:", sat)
        else:
            if log:
                with print_lock:
                    print("Buscando fix (GPS)...")
        time.sleep(SleepTime)

def SaveData():
    with open('./Data/GPS_data.csv', 'a', buffering=1, newline='') as f:
        data_writer = writer(f)
        while True:
            data = data_queue.get()
            data_writer.writerow([
                data["time"].strftime("%d-%m-%Y"),
                data["time"].strftime("%H:%M:%S"),
                data["latitude"],
                data["longitude"],
                data["satellites"]
            ])
