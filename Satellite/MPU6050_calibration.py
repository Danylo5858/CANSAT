import time
import busio
import board
import adafruit_mpu6050

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c)
N = 2000
sum_gx = 0
sum_gy = 0
sum_gz = 0

print("Calibrando... no mover el sensor")

for i in range(N):
	gx, gy, gz = mpu.gyro
	sum_gx += gx
	sum_gy += gy
	sum_gz += gz
	time.sleep(0.001)

bias_x = sum_gx / N
bias_y = sum_gy / N
bias_z = sum_gz / N
print("Bias:", bias_x, bias_y, bias_z)
