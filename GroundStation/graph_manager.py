import requests
import time

air_quality, temperature, humidity, altitude_cansat, temperature_cansat, pressure_cansat = None

def UpdateGraph():
    url = f"https://api.thingspeak.com/update?api_key=BTCDYRXPGC0PZOWK&field1={air_quality}&field2={temperature}&field3={humidity}&field4={altitude_cansat}&field5={temperature_cansat}&field6={pressure_cansat}"
    res = requests.get(url)
    if res.status_code == 200:
        print("Success")
    else:
        print("Error updating data:", res.status_code)

while True:
    UpdateGraph()
    time.sleep(10)
