import time
import requests
from log_manager import log_queue

log = False

def update_graph(name, data):
    if name == "satellite":
        a = data["altitude"]
        t = data["temperature"]
        p = data["pressure"]
        url = f"https://api.thingspeak.com/update?api_key=BTCDYRXPGC0PZOWK&field4={a}&field5={t}&field6={p}"
    elif name == "ground":
        aq = data["air_quality"]
        t = data["temperature"]
        h = data["humidity"]
        url = f"https://api.thingspeak.com/update?api_key=BTCDYRXPGC0PZOWK&field1={aq}&field2={t}&field3={h}"
    try:
        res = requests.get(url)
    except Exception as e:
        if log:
            log_queue.put(f"update_graph [{name}] error: {e}")
    if res and res.status_code == 200 and log:
        log_queue.put(f"Graficos [{name}] actualizados")
        url = "https://api.thingspeak.com/channels/3283442/feeds.json?results=5"
        res = requests.get(url)
        log_queue.put(res)
    elif log:
        if res:
            log_queue.put(f"Error actualizando graficos [{name}]: {res.status_code}")
        else:
            log_queue.put(f"Error actualizando graficos [{name}]")
