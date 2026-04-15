import busio
import board
import adafruit_max1704x

i2c = busio.I2C(board.SCL, board.SDA)

max1704x = adafruit_max1704x.MAX17048(i2c)

while True:
    print(f"{max1704x.cell_percent:.1f}%")
   