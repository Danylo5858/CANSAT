import time
import math
import board
import busio
import adafruit_mpu6050

# =========================================================
# MADGWICK IMU COMPLETO
# =========================================================

class Madgwick:
    def __init__(self, beta=0.12):
        self.beta = beta
        self.q = [1.0, 0.0, 0.0, 0.0]

    def updateIMU(self, gx, gy, gz, ax, ay, az, dt):

        q1, q2, q3, q4 = self.q

        norm = math.sqrt(ax*ax + ay*ay + az*az)
        if norm == 0:
            return self.q
        ax /= norm
        ay /= norm
        az /= norm

        _2q1 = 2.0*q1; _2q2 = 2.0*q2; _2q3 = 2.0*q3; _2q4 = 2.0*q4

        f1 = _2q2*q4 - _2q1*q3 - ax
        f2 = _2q1*q2 + _2q3*q4 - ay
        f3 = 1.0 - _2q2*q2 - _2q3*q3 - az

        grad1 = -_2q3*f1 + _2q2*f2
        grad2 =  _2q4*f1 + _2q1*f2 - 4*q2*f3
        grad3 = -_2q1*f1 + _2q4*f2 - 4*q3*f3
        grad4 =  _2q2*f1 + _2q3*f2

        norm = math.sqrt(grad1*grad1 + grad2*grad2 + grad3*grad3 + grad4*grad4)
        if norm != 0:
            grad1/=norm; grad2/=norm; grad3/=norm; grad4/=norm

        qDot1 = 0.5*(-q2*gx - q3*gy - q4*gz) - self.beta*grad1
        qDot2 = 0.5*( q1*gx + q3*gz - q4*gy) - self.beta*grad2
        qDot3 = 0.5*( q1*gy - q2*gz + q4*gx) - self.beta*grad3
        qDot4 = 0.5*( q1*gz + q2*gy - q3*gx) - self.beta*grad4

        q1 += qDot1*dt
        q2 += qDot2*dt
        q3 += qDot3*dt
        q4 += qDot4*dt

        norm = math.sqrt(q1*q1 + q2*q2 + q3*q3 + q4*q4)
        self.q = [q1/norm, q2/norm, q3/norm, q4/norm]

        return self.q


# =========================================================
# QUATERNION UTILS
# =========================================================

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def normalize(q):
    n = math.sqrt(sum(x*x for x in q))
    return [x/n for x in q]

def q_align(q, ref):
    return [-x for x in q] if dot(q,ref)<0 else q

def q_mean(quats):
    ref = quats[0]
    s = [0,0,0,0]
    for q in quats:
        q = q_align(q, ref)
        for i in range(4):
            s[i]+=q[i]
    return normalize([x/len(quats) for x in s])

# =========================================================
# SLERP
# =========================================================

def slerp(q1, q2, t):
    cos_theta = dot(q1, q2)

    if cos_theta < 0:
        q2 = [-x for x in q2]
        cos_theta = -cos_theta

    if cos_theta > 0.9995:
        return normalize([(1-t)*a + t*b for a,b in zip(q1,q2)])

    theta = math.acos(cos_theta)
    sin_theta = math.sqrt(1 - cos_theta*cos_theta)

    w1 = math.sin((1-t)*theta) / sin_theta
    w2 = math.sin(t*theta) / sin_theta

    return [w1*a + w2*b for a,b in zip(q1,q2)]

# =========================================================
# FORMATO DE SALIDA (REDONDEO SOLO VISUAL)
# =========================================================

def to_xyzw_rounded(q, d=5):
    w, x, y, z = q
    return (round(x,d), round(y,d), round(z,d), round(w,d))

# =========================================================
# SENSOR
# =========================================================

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

madgwick = Madgwick()

# =========================================================
# CONFIG
# =========================================================

FS = 60
DT = 1/FS
WINDOW = 60

buffer = []
last = time.time()

GYRO_THRESHOLD = 0.02

# =========================================================
# LOOP
# =========================================================

while True:
    now = time.time()
    if now - last < DT:
        continue
    last = now

    ax, ay, az = mpu.acceleration
    gx, gy, gz = mpu.gyro

    # anti-drift
    if abs(gx)<GYRO_THRESHOLD and abs(gy)<GYRO_THRESHOLD and abs(gz)<GYRO_THRESHOLD:
        gx *= 0.1
        gy *= 0.1
        gz *= 0.1

    q = madgwick.updateIMU(gx,gy,gz,ax,ay,az,DT)
    buffer.append(q)

    if len(buffer)>=WINDOW:

        N = len(buffer)

        s1 = q_mean(buffer[0:N//4])
        s2 = q_mean(buffer[N//4:N//2])
        s3 = q_mean(buffer[N//2:3*N//4])
        s4 = q_mean(buffer[3*N//4:N])

        q_start = s1
        q_end = s4

        q1 = slerp(q_start, q_end, 0.0)
        q2 = slerp(q_start, q_end, 0.33)
        q3 = slerp(q_start, q_end, 0.66)
        q4 = slerp(q_start, q_end, 1.0)

        print("\n==============================")
        print("Q1:", to_xyzw_rounded(q1))
        print("Q2:", to_xyzw_rounded(q2))
        print("Q3:", to_xyzw_rounded(q3))
        print("Q4:", to_xyzw_rounded(q4))

        buffer = []
