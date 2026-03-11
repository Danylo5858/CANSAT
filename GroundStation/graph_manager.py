import time
import requests
import threading
import asyncio

air_quality = temperature = humidity = altitude_cansat = temperature_cansat = pressure_cansat = None
log = False
SleepTime = 10

print_lock = threading.Lock()

def start():
    while True:
        asyncio.run(main())

async def main():
    t1 = asyncio.create_task(UpdateGraph())
    wait = asyncio.create_task(WaitTime())
    await wait

async def WaitTime():
    await asyncio.sleep(SleepTime)

async def UpdateGraph():
    url = f"https://api.thingspeak.com/update?api_key=BTCDYRXPGC0PZOWK&field1={air_quality}&field2={temperature}&field3={humidity}&field4={altitude_cansat}&field5={temperature_cansat}&field6={pressure_cansat}"
    res = requests.get(url)
    if res.status_code == 200 and log:
        with print_lock:
            print("Success")
    elif log:
        with print_lock:
            print("Error updating data:", res.status_code)
