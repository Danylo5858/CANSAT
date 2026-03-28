from datetime import datetime
from csv import writer
import threading
from queue import Queue
import adafruit_mpu6050
from log_manager import log_queue
from wireless_communication_cansat import buffer

log = False
send_data = False
save_data = False

data_queue = Queue()

def init(i2c, address, lock):
    global mpu, i2c_lock
    i2c_lock = lock
    mpu = adafruit_mpu6050.MPU6050(i2c, address=address)
    if save_data:
        threading.Thread(target=SaveData, daemon=True).start()

def GetData():
    with i2c_lock:
        gyro = mpu.gyro
    if log:
        log_queue.put(f"Giroscopio: {gyro}")
    if send_data:
        buffer.append({
            "gyro": gyro
        })
    data = {
        "time": datetime.now(),
        "gyro": gyro
    }
    data_queue.put(data)

def SaveData():
    with open('./Data/MPU6050_data.csv', 'a', buffering=1, newline='') as f:
        data_writer = writer(f)
        while True:
            data = data_queue.get()
            data_writer.writerow([
                data["time"].strftime("%d-%m-%Y"),
                data["time"].strftime("%H:%M:%S"),
                data["gyro"]
            ])
