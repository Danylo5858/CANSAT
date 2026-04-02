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

data_queue = Queue()

def init(i2c, address, lock):
    global mpu, i2c_lock
    i2c_lock = lock
    mpu = adafruit_mpu6050.MPU6050(i2c, address=address)
    if save_data:
        threading.Thread(target=SaveData, daemon=True).start()

def GetData():
    quats = update_motion_state()
    if send_data:
        buffer["MPU6050"] = quats
    data = {
        "time": datetime.now(),
        "quats": quats
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
                data["quats"]
            ])

def update_motion_state():
    FS = 60
    DT = 1/FS
    WINDOW = 60
    GYRO_THRESHOLD = 0.02
    buffer = []
    last = time.time()
    madgwick = utils.Madgwick()

    while True:
        now = time.time()
        if now - last < DT:
            continue
        last = now

        with i2c_lock:
            ax, ay, az = mpu.acceleration
            gx, gy, gz = mpu.gyro

        gx -= utils.BIAS_GX
        gy -= utils.BIAS_GY
        gz -= utils.BIAS_GZ

        ax -= utils.BIAS_AX
        ay -= utils.BIAS_AY
        az -= utils.BIAS_AZ

        if abs(gx)<GYRO_THRESHOLD and abs(gy)<GYRO_THRESHOLD and abs(gz)<GYRO_THRESHOLD:
            gx *= 0.1
            gy *= 0.1
            gz *= 0.1

        q = madgwick.updateIMU(gx, gy, gz, ax, ay, az, DT)
        buffer.append(q)

        if len(buffer) >= WINDOW:

            N = len(buffer)

            s1 = utils.q_mean(buffer[0:N//4])
            s2 = utils.q_mean(buffer[N//4:N//2])
            s3 = utils.q_mean(buffer[N//2:3*N//4])
            s4 = utils.q_mean(buffer[3*N//4:N])

            q_start = s1
            q_end = s4

            q1 = utils.slerp(q_start, q_end, 0.0)
            q2 = utils.slerp(q_start, q_end, 0.25)
            q3 = utils.slerp(q_start, q_end, 0.5)
            q4 = utils.slerp(q_start, q_end, 1.75)

            r1 = utils.to_xyzw_rounded(q1)
            r2 = utils.to_xyzw_rounded(q2)
            r3 = utils.to_xyzw_rounded(q3)
            r4 = utils.to_xyzw_rounded(q4)

            if log:
                log_queue.put(f"MPU6050:\nQ1: {r1}\nQ2: {r2}\nQ3: {r3}\nQ4: {r4}")
            buffer = []
            return [r1, r2, r3, r4]
