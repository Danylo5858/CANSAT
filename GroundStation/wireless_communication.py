import threading
from sx126x import SX126X, Address

log = False

print_lock = threading.Lock()

def start():
    print("init")
    lora = SX126X(Address(1, 1))
    while True:
        print("TEST")
        addr, data = lora.rx()
        if log:
            with print_lock:
                print(f"Recibido de {addr}: {data}")
