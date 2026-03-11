import time
import requests
import threading
import asyncio
import openmeteo_requests
import graph_manager as gm

openmeteo = openmeteo_requests.Client()
log = False
SleepTime = 10

print_lock = threading.Lock()

def start():
    while True:
        asyncio.run(main())

async def main():
    t1 = asyncio.create_task(GetAirQuality())
    t2 = asyncio.create_task(GetTemperatureAndHumidity())
    wait = asyncio.create_task(WaitTime())
    await wait

async def WaitTime():
    await asyncio.sleep(SleepTime)

async def GetAirQuality():
    global air_quality, latitude, longitude
    url = "https://api.waqi.info/feed/@6779/?token=db94e4c768d260335021f2dbc8dfc088345d6bab"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        air_quality = data["data"]["aqi"]
        latitude = int(data["data"]["city"]["geo"][0])
        longitude = int(data["data"]["city"]["geo"][1])
        gm.air_quality = air_quality
        if log:
            with print_lock:
                print("Calidad del aire:", air_quality)
    else:
        gm.air_quality = None
        if log:
            with print_lock:
                print("Error fetching air quality:", res.status_code)

async def GetTemperatureAndHumidity():
    global temperature, humidity
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["temperature_2m", "relative_humidity_2m"]
    }
    res = openmeteo.weather_api(url, params=params)
    current = res[0].Current()
    temperature = round(current.Variables(0).Value())
    humidity = round(current.Variables(1).Value())
    gm.temperature = temperature
    gm.humidity = humidity
    if log:
        with print_lock:
            print("Temperatura:", str(temperature) + " C")
            print("Humedad:", str(humidity) + "%")
