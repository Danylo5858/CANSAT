import time
import requests
import threading
import asyncio
import openmeteo_requests

openmeteo = openmeteo_requests.Client()
log = False
SleepTime = 10

print_lock = threading.Lock()

def start():
    while True:
        asyncio.run(asyncio.gather(GetAirQuality(), GetTemperatureAndHumidity()))
        time.sleep(SleepTime)

async def GetAirQuality():
    global air_quality, latitude, longitude
    url = "https://api.waqi.info/feed/@6779/?token=db94e4c768d260335021f2dbc8dfc088345d6bab"
    res = requests.get(url)
    if res.status_code == 200 and log:
        data = res.json()
        air_quality = data["data"]["aqi"]
        latitude = int(data["data"]["city"]["geo"][0])
        longitude = int(data["data"]["city"]["geo"][1])
        with print_lock:
            print("Calidad del aire:", air_quality)
    elif log:
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
    if log:
        with print_lock:
            print("Temperatura:", str(temperature) + " C")
            print("Humedad:", str(humidity) + "%")
