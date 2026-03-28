import time
import json
import threading
import graph_manager as gm
import weather_data_fetcher as wdf
import wireless_communication_gs as wcom_gs
from sx126x import sx126x

GlobalSleepTime = 5

wdf.SleepTime = GlobalSleepTime
wdf.log = True
#threading.Thread(target=wdf.start, daemon=False).start()

gm.SleepTime = GlobalSleepTime
gm.log = True
#threading.Thread(target=gm.start, daemon=False).start()

#threading.Thread(target=wcom.start, daemon=False).start()

radio = sx126x("/dev/serial0", 868, 0x0002, 22, True)

while True:
	data = radio.receive()
	print(json.loads(data))
	time.sleep(0.5)
