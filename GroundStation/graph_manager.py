import time
import requests
from log_manager import log_queue

log = False

def update_graph(data):
    air_quality_g = None
    temperature_g = None
    humidity_g = None
    altitude_c = data["altitude"]
    temperature_c = data["temperature"]
    pressure_c = data["pressure"]
    url = f"https://api.thingspeak.com/update?api_key=BTCDYRXPGC0PZOWK&field1={air_quality_g}&field2={temperature_g}&field3={humidity_g}&field4={altitude_c}&field5={temperature_c}&field6={pressure_c}"
    res = requests.get(url)
    if res.status_code == 200 and log:
        log_queue.put("Grafico actualizado")
    elif log:
        log_queue.put(f"Error actualizando grafico: {res.status_code}")
