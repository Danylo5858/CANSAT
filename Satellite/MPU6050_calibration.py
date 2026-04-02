import time
import busio
import board
import adafruit_mpu6050

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)

N = 2000

sum_gx = sum_gy = sum_gz = 0
sum_ax = sum_ay = sum_az = 0

print("Calibrando... NO mover el sensor")

for i in range(N):
    gx, gy, gz = mpu.gyro
    ax, ay, az = mpu.acceleration

    sum_gx += gx
    sum_gy += gy
    sum_gz += gz

    sum_ax += ax
    sum_ay += ay
    sum_az += az

    time.sleep(0.001)

# =========================================================
# GYRO BIAS
# =========================================================
bias_gx = sum_gx / N
bias_gy = sum_gy / N
bias_gz = sum_gz / N

# =========================================================
# ACCEL BIAS (NO GRAVITY REMOVAL)
# =========================================================
bias_ax = sum_ax / N
bias_ay = sum_ay / N
bias_az = sum_az / N

print("\n===== RESULTADOS =====")

print("\nGYRO BIAS:")
print(bias_gx, bias_gy, bias_gz)

print("\nACCEL BIAS:")
print(bias_ax, bias_ay, bias_az)
