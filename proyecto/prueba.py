import sx126x
import time
import base64
from PIL import Image
import io

node = sx126x.sx126x(serial_num = "/dev/ttyS0",freq=868,addr=0,power=22,rssi=False,air_speed=2400,relay=False)

while True:
    result = node.receive()
    if result is not None:
        resultado = base64.b64decode(result)
        final = Image.open(io.BytesIO(resultado))
