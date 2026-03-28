import time
import threading
import graph_manager as gm
import weather_data_fetcher as wdf
import log_manager as lm
import wireless_communication_gs as wcom_gs

GlobalSleepTime = 1

threading.Thread(target=lm.logger, daemon=True).start()

wcom_gs.log = True
wcom_gs.init(2, 868)
threading.Thread(target=wcom_gs.receiver, daemon=True).start()

wdf.log = True
gm.log = True

while True:
	data = wcom_gs.received_data.get()
	threads = [
		threading.Thread(target=gm.UpdateGraph, args=(data["BMP390"],), daemon=True)
	]
	for t in threads:
		t.start()
	for t in threads:
		t.join()
