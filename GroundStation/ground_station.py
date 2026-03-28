import threading
import graph_manager as gm
import weather_data_fetcher as wdf
import wireless_communication_gs as wcom_gs

GlobalSleepTime = 5

wdf.SleepTime = GlobalSleepTime
wdf.log = True
#threading.Thread(target=wdf.start, daemon=False).start()

gm.SleepTime = GlobalSleepTime
gm.log = True
#threading.Thread(target=gm.start, daemon=False).start()

wcom.log = True
#threading.Thread(target=wcom.start, daemon=False).start()

def OnReceive(data):
	print(data)

wcom_gs.start_listener(OnReceive)
