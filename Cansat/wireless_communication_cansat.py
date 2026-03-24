#from sx126x import SX126X, Address

#print("a")
#lora = SX126X(Address(1, 2))
#receiver = Address(1, 1)
#print("b", flush=True)
#lora.tx(receiver, "1234")
#print("c")

#def send(data):
#    print("SENDING...")
#    lora = SX126X(Address(1, 2))
#    receiver = Address(1, 1)
#    lora.tx(receiver, data)
#    print("SENT")
#    return f"Enviado a {receiver}: {data.decode()}"

import sx126x as sx126x
import time

lora = sx126x.sx126x("/dev/ttyS0", freq=868, addr=1, power=22)

while True:
    lora.send("2,868,CANSAT")
    print("Enviado")
    time.sleep(3)
