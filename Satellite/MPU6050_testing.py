import time
import numpy as np
import board
import busio
import adafruit_mpu6050
from ahrs.filters import Madgwick

# -----------------------------
# Sensor setup
# -----------------------------
i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c, address=0x68)

# -----------------------------
# Madgwick
# -----------------------------
madgwick = Madgwick()
q = np.array([1.0, 0.0, 0.0, 0.0])

# -----------------------------
# Config
# -----------------------------
FS = 60
DT = 1.0 / FS
WINDOW = 60

buffer = []

# -----------------------------
# Quaternion alignment
# -----------------------------
def align(q, ref):
    if np.dot(q, ref) < 0:
        return -q
    return q

# -----------------------------
# Quaternion mean (robusto)
# -----------------------------
def mean_quaternions(Q):
    Q = np.array(Q)

    ref = Q[0]
    Q_aligned = np.array([align(q, ref) for q in Q])

    mean = np.mean(Q_aligned, axis=0)
    return mean / np.linalg.norm(mean)

# -----------------------------
# Segment average
# -----------------------------
def segment_mean(data, start, end):
    seg = data[start:end]
    if len(seg) == 0:
        return None
    return mean_quaternions(seg)

# -----------------------------
# Loop
# -----------------------------
last = time.time()

while True:
    now = time.time()
    if now - last < DT:
        continue
    last = now

    accel = np.array(mpu.acceleration)
    gyro = np.array(mpu.gyro)

    accel = accel / np.linalg.norm(accel)

    q = madgwick.updateIMU(q, gyr=gyro, acc=accel)

    if q is None:
        continue

    buffer.append(q.copy())

    if len(buffer) >= WINDOW:

        N = len(buffer)

        # 4 segmentos
        s1 = segment_mean(buffer, 0, N//4)
        s2 = segment_mean(buffer, N//4, N//2)
        s3 = segment_mean(buffer, N//2, 3*N//4)
        s4 = segment_mean(buffer, 3*N//4, N)

        print("\n=== 4 QUATERNIONS PROMEDIADOS ===")
        print("Q1:", s1)
        print("Q2:", s2)
        print("Q3:", s3)
        print("Q4:", s4)

        buffer = []
