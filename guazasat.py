import time
from datetime import datetime
from csv import writer
import board
import busio
import adafruit_bmp3xx
import RPi.GPIO as GPIO


i2c = busio.I2C(board.SCL, board.SDA)
print("Devices: ", [hex(device_address) for device_address in i2c.scan()])
bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c, address=0x68)

bmp.pressure_oversampling = 8
bmp.temperature_oversampling = 2
bmp.sea_level_pressure = 1013.25

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT) # LED
GPIO.setup(15, GPIO.OUT) # BUZZER
GPIO.output(17, GPIO.HIGH)

def get_data():
    data = []
    data.append(datetime.now().strftime("%d-%m-%Y"))
    data.append(datetime.now().strftime("%H:%M:%S"))
    data.append(bmp.temperature)
    data.append(bmp.pressure)
    data.append(bmp.altitude)
    return data

with open('data.csv', 'a', buffering=1, newline='') as f:
    data_writer = writer(f)
    while True:
        data = get_data()
        data_writer.writerow(data)
        print(data)
        GPIO.output(15, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(15, GPIO.LOW)
