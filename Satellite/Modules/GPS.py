import time
from datetime import datetime
from csv import writer
import threading
from queue import Queue
import adafruit_gps
from log_manager import log_queue
from wireless_communication_cansat import msg_queue

log = False
save_data = False
send_data = False
SleepTime = 1

data_queue = Queue()

def init(i2c, address, lock):
    global gps, i2c_lock
    i2c_lock = lock
    gps = adafruit_gps.GPS_GtopI2C(i2c, address=address)
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    gps.send_command(b"PMTK220,1000")
    threading.Thread(target=start, daemon=True).start()
    if save_data:
        threading.Thread(target=SaveData, daemon=True).start()

def start():
    while True:
        gps.update()
        if gps.has_fix:
            with i2c_lock:
                lan = gps.latitude
                lon = gps.longitude
                sat = gps.satellites
            data = {
                "latitude": lan,
                "longitude": lon,
                "satellites": sat
            }
            if send_data:
                msg_queue.put(data)
            timestamp = datetime.now()
            data["time"] = timestamp
            data_queue.put(data)
            if log:
                log_queue.put(f"Lat: {lan:.4f}\nLon: {lon:.4f}\nSatelites: {sat}")
        else:
            data = {
                "latitude": 0,
                "longitude": 0,
                "satellites": 0
            }
            if send_data:
                msg_queue.put(data)
            if log:
                log_queue.put("Buscando fix (GPS)...")
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
