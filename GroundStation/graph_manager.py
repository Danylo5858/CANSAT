import time
import requests
from log_manager import log_queue

log = False

def update_graph(cansat_data, ground_data):
    a_c = cansat_data["altitude"]
    t_c = cansat_data["temperature"]
    p_c = cansat_data["pressure"]
    aq_g = ground_data["air_quality"]
    t_g = ground_data["temperature"]
    h_g = ground_data["humidity"]
    url = f"https://api.thingspeak.com/update?api_key=BTCDYRXPGC0PZOWK&field1={aq_g}&field2={t_g}&field3={h_g}&field4={a_c}&field5={t_c}&field6={p_c}"
    res = None
    try:
        res = requests.get(url)
    except Exception as e:
        if log:
            log_queue.put(f"Error updating graph: {e}")
    if res and res.status_code == 200 and log:
        log_queue.put(f"Graficos actualizados")
    elif log:
        if res:
            log_queue.put(f"Error updating graph: {res.status_code}")
        else:
            log_queue.put(f"Error updating graph")
