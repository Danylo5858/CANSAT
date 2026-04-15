import board
import adafruit_max1704x

i2c = board.I2C()

max1704x = adafruit_max1704x.MAX17048(i2c)

while True:
    print(f"Voltaje: {max1704x.cell_voltage:.2f} V")
    print(f"Batería: {max1704x.cell_percent:.1f} %")
    print("----")
