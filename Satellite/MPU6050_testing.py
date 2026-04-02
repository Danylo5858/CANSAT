import time
import math
import board
import busio
import adafruit_mpu6050

# =========================================================
# MADGWICK IMU COMPLETO (SIN NUMPY)
# =========================================================

class Madgwick:
    def __init__(self, beta=0.12):
        self.beta = beta
        self.q1 = 1.0
        self.q2 = 0.0
        self.q3 = 0.0
        self.q4 = 0.0

    def updateIMU(self, gx, gy, gz, ax, ay, az, dt):

        q1, q2, q3, q4 = self.q1, self.q2, self.q3, self.q4

        # ---- normalizar acelerómetro ----
        norm = math.sqrt(ax*ax + ay*ay + az*az)
        if norm == 0:
            return (q1, q2, q3, q4)
        ax /= norm
        ay /= norm
        az /= norm

        # ---- gradient descent ----
        _2q1 = 2.0 * q1
        _2q2 = 2.0 * q2
        _2q3 = 2.0 * q3
        _2q4 = 2.0 * q4

        f1 = _2q2*q4 - _2q1*q3 - ax
        f2 = _2q1*q2 + _2q3*q4 - ay
        f3 = 1.0 - _2q2*q2 - _2q3*q3 - az

        J_11 = -_2q3
        J_12 =  _2q4
        J_13 = -_2q1
        J_14 =  _2q2

        J_21 =  _2q2
        J_22 =  _2q1
        J_23 =  _2q4
        J_24 =  _2q3

        J_31 =  0.0
        J_32 = -4.0*q2
        J_33 = -4.0*q3
        J_34 =  0.0

        grad1 = J_11*f1 + J_21*f2 + J_31*f3
        grad2 = J_12*f1 + J_22*f2 + J_32*f3
        grad3 = J_13*f1 + J_23*f2 + J_33*f3
        grad4 = J_14*f1 + J_24*f2 + J_34*f3

        norm = math.sqrt(grad1*grad1 + grad2*grad2 + grad3*grad3 + grad4*grad4)
        if norm != 0:
            grad1 /= norm
            grad2 /= norm
            grad3 /= norm
            grad4 /= norm

        # ---- integración gyro ----
        qDot1 = 0.5 * (-q2*gx - q3*gy - q4*gz) - self.beta * grad1
        qDot2 = 0.5 * ( q1*gx + q3*gz - q4*gy) - self.beta * grad2
        qDot3 = 0.5 * ( q1*gy - q2*gz + q4*gx) - self.beta * grad3
        qDot4 = 0.5 * ( q1*gz + q2*gy - q3*gx) - self.beta * grad4

        q1 += qDot1 * dt
        q2 += qDot2 * dt
        q3 += qDot3 * dt
        q4 += qDot4 * dt

        # normalizar quaternion
        norm = math.sqrt(q1*q1 + q2*q2 + q3*q3 + q4*q4)
        self.q1 = q1 / norm
        self.q2 = q2 / norm
        self.q3 = q3 / norm
        self.q4 = q4 / norm

        return (self.q1, self.q2, self.q3, self.q4)


# =========================================================
# QUATERNION UTILITIES
# =========================================================

def q_align(q, ref):
    if (q[0]*ref[0] + q[1]*ref[1] + q[2]*ref[2] + q[3]*ref[3]) < 0:
        return (-q[0], -q[1], -q[2], -q[3])
    return q

def q_mean(quats):
    if not quats:
        return None

    ref = quats[0]
    sx = sy = sz = sw = 0.0

    for q in quats:
        q = q_align(q, ref)
        sx += q[0]
        sy += q[1]
        sz += q[2]
        sw += q[3]

    n = len(quats)
    norm = math.sqrt((sx/n)**2 + (sy/n)**2 + (sz/n)**2 + (sw/n)**2)
    return (sx/(n*norm), sy/(n*norm), sz/(n*norm), sw/(n*norm))


# =========================================================
# SENSOR SETUP
# =========================================================

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

madgwick = Madgwick(beta=0.12)

# =========================================================
# CONFIG
# =========================================================

FS = 60.0
DT = 1.0 / FS
WINDOW = 60

buffer = []

last = time.time()

# =========================================================
# LOOP PRINCIPAL
# =========================================================

while True:
    now = time.time()
    if now - last < DT:
        continue
    last = now

    # ---- lectura sensor ----
    ax, ay, az = mpu.acceleration
    gx, gy, gz = mpu.gyro

    # ---- filtro ----
    q = madgwick.updateIMU(gx, gy, gz, ax, ay, az, DT)
    buffer.append(q)

    # ---- 4 quaternions clave ----
    if len(buffer) >= WINDOW:

        N = len(buffer)

        def seg(a, b):
            return q_mean(buffer[a:b])

        q1 = seg(0, N//4)
        q2 = seg(N//4, N//2)
        q3 = seg(N//2, 3*N//4)
        q4 = seg(3*N//4, N)

        print("\n==============================")
        print("Q1 START :", q1)
        print("Q2 25%   :", q2)
        print("Q3 50%   :", q3)
        print("Q4 END   :", q4)

        buffer = []
