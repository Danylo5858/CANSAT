import adafruit_mpu6050
import board
import busio

i2c = busio.I2C(board.SCL, board.SDA)
mpu = adafruit_mpu6050.MPU6050(i2c, address=0x68)

while True:
	print(mpu.gyro)
