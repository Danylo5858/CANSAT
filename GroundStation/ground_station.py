import threading
import graph_manager as gm
import weather_data_fetcher as wdf
import log_manager as lm
import wireless_communication_gs as wcom_gs

threading.Thread(target=lm.logger, daemon=True).start()

GlobalSleepTime = 5

wdf.SleepTime = GlobalSleepTime
wdf.log = True
#threading.Thread(target=wdf.start, daemon=False).start()

gm.SleepTime = GlobalSleepTime
gm.log = True
#threading.Thread(target=gm.start, daemon=False).start()

wcom_gs.log = True
wcom_gs.init(2, 868)

threading.Thread(target=wcom_gs.receiver, daemon=False).start()
