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

#def GetData():
#    with i2c_lock:
#        gx, gy, gz = [round(v, 5) for v in mpu.gyro]
#    gyro = [gx, gy, gz]
#    if log:
#        log_queue.put(f"Giroscopio: {gyro}")
#    if send_data:
#        buffer["MPU6050"] = {
#            "gyro": gyro
#        }
#        #buffer.append(gyro)
#    data = {
#        "time": datetime.now(),
#        "gyro": gyro
#    }
#    data_queue.put(data)

def GetData():
    packet = update_motion_state()
    if send_data:
        buffer["MPU6050_BIN"] = packet

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


FS = 60
DT = 1/FS
WINDOW = 60
GYRO_THRESHOLD = 0.02
buffer = []
last = time.time()
madgwick = utils.Madgwick()

def update_motion_state():
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

            if log:
                log_queue.put(f"MPU6050:\nQ1: {utils.to_xyzw_rounded(q1)}\nQ2: {utils.to_xyzw_rounded(q2)}\nQ3: {utils.to_xyzw_rounded(q3)}\nQ4: {utils.to_xyzw_rounded(q4)}")

            buffer = []
            return None


# SAMPLE_RATE = 60
# DT = 1.0 / SAMPLE_RATE
# deg_to_rad = np.pi / 180.0

# def quat_mul(a, b):
#     w1, x1, y1, z1 = a
#     w2, x2, y2, z2 = b
#     return np.array([
#         w1*w2 - x1*x2 - y1*y2 - z1*z2,
#         w1*x2 + x1*w2 + y1*z2 - z1*y2,
#         w1*y2 - x1*z2 + y1*w2 + z1*x2,
#         w1*z2 + x1*y2 - y1*x2 + z1*w2
#     ])

# def gyro_to_quat(gx, gy, gz):
#     gx *= deg_to_rad
#     gy *= deg_to_rad
#     gz *= deg_to_rad
#     half_dt = DT / 2.0
#     return np.array([
#         1.0,
#         gx * half_dt,
#         gy * half_dt,
#         gz * half_dt
#     ])

# def normalize(q):
#     return q / np.linalg.norm(q)

# def update_motion_state():
#     q = np.array([1.0, 0.0, 0.0, 0.0])
#     buffer = []

#     for _ in range(SAMPLE_RATE):
#         with i2c_lock:
#             gyro = mpu.gyro
#             accel = mpu.acceleration
#         gx, gy, gz = gyro
#         dq = gyro_to_quat(gx, gy, gz)
#         q = quat_mul(q, dq)
#         q = normalize(q)
#         buffer.append(q.copy())
#         if len(buffer) > SAMPLE_RATE:
#             buffer.pop(0)
#         time.sleep(DT)

#     packet = bytearray()
#     for q in buffer:
#         for v in q:
#             packed = int(v * 32767)
#             packet += struct.pack('<h', packed)
#     if log:
#         log_queue.put(f"Paquete MPU6050 comprimido y listo para enviar: {len(packet)} bytes")
#     return packet
