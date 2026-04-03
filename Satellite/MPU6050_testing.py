import time
import math
import board
import busio
import adafruit_mpu6050

# =========================================================
# GYRO BIAS ONLY
# =========================================================

BIAS_GX = -0.05587
BIAS_GY = 0.04214
BIAS_GZ = -0.00273

# =========================================================
# MADGWICK
# =========================================================

class Madgwick:
    def __init__(self, beta=0.08):
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

        _2q1 = 2*q1
        _2q2 = 2*q2
        _2q3 = 2*q3
        _2q4 = 2*q4

        f1 = _2q2*q4 - _2q1*q3 - ax
        f2 = _2q1*q2 + _2q3*q4 - ay
        f3 = 1 - _2q2*q2 - _2q3*q3 - az

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
# UTILS
# =========================================================

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def normalize(q):
    n = math.sqrt(sum(x*x for x in q))
    return [x/n for x in q]

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


def quat_conj(q):
    w,x,y,z = q
    return [w, -x, -y, -z]

def quat_mul(a,b):
    aw,ax,ay,az = a
    bw,bx,by,bz = b

    return [
        aw*bw - ax*bx - ay*by - az*bz,
        aw*bx + ax*bw + ay*bz - az*by,
        aw*by - ax*bz + ay*bw + az*bx,
        aw*bz + ax*by - ay*bx + az*bw
    ]


# =========================================================
# SENSOR
# =========================================================

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

madgwick = Madgwick()

FS = 60
DT = 1/FS

last = time.time()
buffer = []

q_ref = None


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

    gx -= BIAS_GX
    gy -= BIAS_GY
    gz -= BIAS_GZ

    q = madgwick.updateIMU(gx, gy, gz, ax, ay, az, DT)

    # guardar referencia inicial (CLAVE)
    if q_ref is None:
        q_ref = q.copy()

    # convertir a world-lock (quita inclinación fantasma)
    q_world = quat_mul(quat_conj(q_ref), q)

    buffer.append(q_world)

    # =====================================================
    # DETECTAR ESTADO QUIETO (auto-stabilization)
    # =====================================================

    still = abs(gx) + abs(gy) + abs(gz) < 0.06

    if still and len(buffer) > 10:
        # recentrar suavemente
        q_world = buffer[-1]

    # =====================================================
    # OUTPUT SMOOTH
    # =====================================================

    if len(buffer) >= 30:

        def mean_quat(quats):
            ref = quats[0]
            s = [0,0,0,0]
            for q in quats:
                if dot(q, ref) < 0:
                    q = [-x for x in q]
                for i in range(4):
                    s[i] += q[i]
            n = len(quats)
            return normalize([x/n for x in s])

        q1 = mean_quat(buffer[:10])
        q2 = mean_quat(buffer[10:20])
        q3 = mean_quat(buffer[20:30])

        print("\n===================")
        print("Q:", [round(x,4) for x in q3])

        buffer = []
