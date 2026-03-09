import time
from datetime import datetime
from csv import writer
import threading
import adafruit_gps

log = False
SleepTime = 1

print_lock = threading.Lock()

def init(i2c, address):
    global gps
    gps = adafruit_gps.GPS_GtopI2C(i2c, address=address)
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
    gps.send_command(b"PMTK220,1000")
    threading.Thread(target=start, daemon=True).start()

def start():
    while True:
        gps.update()
        if gps.has_fix:
            if log:
                with print_lock:
                    print("Lat:", f"{gps.latitude:.4f}")
                    print("Lon:", f"{gps.longitude:.4f}")
                    print("Satelites:", gps.satellites)
        else:
            if log:
                with print_lock:
                    print("Buscando fix (GPS)...")
        time.sleep(SleepTime)

def SaveData(frequency):
    with open('./Data/GPS_data.csv', 'a', buffering=1, newline='') as f:
        data_writer = writer(f)
        while True:
            data = GetData()
            data_writer.writerow(data)
            time.sleep(frequency)

def GetData():
    data = []
    data.append(datetime.now().strftime("%d-%m-%Y"))
    data.append(datetime.now().strftime("%H:%M:%S"))
    if gps.has_fix:
        data.append(f"{gps.latitude:.4f}")
        data.append(f"{gps.longitude:.4f}")
        data.append(gps.satellites)
    else:
        data.append("Waiting for fix...")
    return data
