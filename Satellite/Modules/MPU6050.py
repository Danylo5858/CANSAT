import time
from datetime import datetime
from csv import writer
import threading
from queue import Queue
import struct
import numpy as np
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
        gx, gy, gz = [round(v, 5) for v in mpu.gyro]
    gyro = [gx, gy, gz]
    if log:
        log_queue.put(f"Giroscopio: {gyro}")
    if send_data:
        buffer["MPU6050"] = {
            "gyro": gyro
        }
        #buffer.append(gyro)
    data = {
        "time": datetime.now(),
        "gyro": gyro
    }
    data_queue.put(data)
    update_motion_state()

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

def update_motion_state():
    global packet

    SAMPLE_RATE = 60
    DT = 1.0 / SAMPLE_RATE
    ALPHA = 0.98
    deg_to_rad = np.pi / 180.0
    q = np.array([1.0, 0.0, 0.0, 0.0])
    buffer = []

    def quat_mul(a, b):
        w1, x1, y1, z1 = a
        w2, x2, y2, z2 = b
        return np.array([
            w1*w2 - x1*x2 - y1*y2 - z1*z2,
            w1*x2 + x1*w2 + y1*z2 - z1*y2,
            w1*y2 - x1*z2 + y1*w2 + z1*x2,
            w1*z2 + x1*y2 - y1*x2 + z1*w2
        ])

    def gyro_to_quat(gx, gy, gz):
        gx *= deg_to_rad
        gy *= deg_to_rad
        gz *= deg_to_rad
        half_dt = DT / 2.0
        return np.array([
            1.0,
            gx * half_dt,
            gy * half_dt,
            gz * half_dt
        ])

    def normalize(q):
        return q / np.linalg.norm(q)

    while True:
        for _ in range(SAMPLE_RATE):
            with i2c_lock:
                gyro = mpu.gyro
                accel = mpu.acceleration
            gx, gy, gz = gyro
            dq = gyro_to_quat(gx, gy, gz)
            q = quat_mul(q, dq)
            q = normalize(q)
            buffer.append(q.copy())
            if len(buffer) > SAMPLE_RATE:
                buffer.pop(0)
            time.sleep(DT)

        packet = bytearray()
        for q in buffer:
            for v in q:
                packed = int(v * 32767)
                packet += struct.pack('<h', packed)
        buffer.clear()
        if log:
            log_queue.put(f"Paquete MPU6050 comprimido y listo para enviar: {len(packet)} bytes")
