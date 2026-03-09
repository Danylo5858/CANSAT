import threading
import graph_manager as gm
import weather_data_fetcher as wdf

GlobalSleepTime = 5

wdf.SleepTime = GlobalSleepTime
wdf.log = True
threading.Thread(target=wdf.start, daemon=True).start()

gm.SleepTime = GlobalSleepTime
gm.log = True
threading.Thread(target=gm.start, daemon=True).start()
