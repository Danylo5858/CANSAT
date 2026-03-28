import time
import json
import threading
from sx126x import sx126x
import wireless_communication_gs as wcom_gs
import graph_manager as gm
import weather_data_fetcher as wdf
import log_manager as lm
from log_manager import log_queue

threading.Thread(target=lm.logger, daemon=True).start()

GlobalSleepTime = 5

wdf.SleepTime = GlobalSleepTime
wdf.log = True
#threading.Thread(target=wdf.start, daemon=False).start()

gm.SleepTime = GlobalSleepTime
gm.log = True
#threading.Thread(target=gm.start, daemon=False).start()

#threading.Thread(target=wcom.start, daemon=False).start()

def OnReceive(data):
	log_queue.put(data)

radio = sx126x("/dev/serial0", 868, 2, 22, False)

while True:
	radio.receive(OnReceive)
	time.sleep(0.5)
