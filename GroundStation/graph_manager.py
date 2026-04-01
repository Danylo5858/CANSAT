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
    res = requests.get(url)
    if res.status_code == 200 and log:
        log_queue.put(f"Graficos [{name}] actualizados")
    elif log:
        log_queue.put(f"Error actualizando graficos [{name}]: {res.status_code}")
