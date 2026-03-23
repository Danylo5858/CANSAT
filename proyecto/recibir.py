import sx126x
import time

node = sx126x.sx126x(serial_num = "/dev/ttyS0",freq=868,addr=0,power=22,rssi=False,air_speed=2400,relay=False)

result = node.receive()

while True:
    with open('archivo.txt', 'w') as archivo:
        resultado = str(node.receive())
        
        archivo.write(resultado)
