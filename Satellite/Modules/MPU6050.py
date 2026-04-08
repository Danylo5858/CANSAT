import time
from datetime import datetime
from csv import writer
import threading
from queue import Queue
import struct
import numpy as np
import adafruit_mpu6050
import MPU6050_utils as utils
from log_manager import log_queue
from wireless_communication_cansat import buffer

log = False
send_data = False
save_data = False
buffering_time = 1

data_queue = Queue()

def init(i2c, address, lock):
    global mpu, i2c_lock
    i2c_lock = lock
    mpu = adafruit_mpu6050.MPU6050(i2c, address=address)
    if save_data:
        threading.Thread(target=SaveData, daemon=True).start()
    threading.Thread(target=update_motion_state, daemon=True).start()

def GetData():
    time.sleep(buffering_time)
    buffer_data = process_buffer_data()
    if send_data:
        buffer["MPU6050"] = buffer_data
    data = {
        "time": datetime.now(),
        "accel": buffer_data["accel"]
    }
    data_queue.put(data)

def SaveData():
    with open('./Data/MPU6050_data.csv', 'a', buffering=1, newline='') as f:
        data_writer = writer(f)
        while True:
            data = data_queue.get()
            data_writer.writerow([
                data["time"].strftime("%Y-%m-%d"),
                data["time"].strftime("%H:%M:%S"),
                data["accel"]
            ])

def update_motion_state():
    global accel_buffer
    global buffer_start
    accel_buffer = []
    FS = 60
    DT = buffering_time/FS
    while True:
        if accel_buffer == []:
            buffer_start = time.time()
        with i2c_lock:
            ax, ay, az = mpu.acceleration
        # CÁLCULO DE ACCEL BIAS
        accel_buffer.append([ax, ay, az])
        time.sleep(DT)

def process_buffer_data():
    points = utils.extract_representative_points(accel_buffer)
    points_rounded = utils.round_points(points)
    accel_buffer.clear()
    data = {
        "time": time.time() * 10000,
        "accel": points_rounded
    }
    if log:
        log_queue.put(f"MPU6050: {data}")
    return data
