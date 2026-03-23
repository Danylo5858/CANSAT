#import threading
#from sx126x import SX126X, Address

#log = False

#print_lock = threading.Lock()

#def start():
#    print("init")
#    lora = SX126X(Address(1, 1))
#    while True:
#        print("TEST")
#        addr, data = lora.rx()
#        if log:
#            with print_lock:
#                print(f"Recibido de {addr}: {data}")

#start()

import sx126x
import time

lora = sx126x.sx126x("/dev/ttyS0", freq=868, addr=2, power=22)

while True:
    data = lora.receive()
    if data:
        print("Recibido:", data)
    time.sleep(0.5)
