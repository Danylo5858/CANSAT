import time
#from concurrent.futures import ThreadPoolExecutor
import requests
import openmeteo_requests
from log_manager import log_queue

log = False
lat = 0
lon = 0

token = "db94e4c768d260335021f2dbc8dfc088345d6bab"

def init():
    global openmeteo
    try:
        openmeteo = openmeteo_requests.Client()
    except Exception as e:
        if log:
            log_queue.put(f"weather_data_fetcher init error: {e}")

def GetAirQuality():
    if lat == 0 and lon == 0:
        url = f"https://api.waqi.info/feed/@6779/?token={token}"
    else:
        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={token}"
    try:
        res = requests.get(url)
    except Exception as e:
        if log:
            log_queue.put(f"GetAirQuality Error: {e}")
    if res and res.status_code == 200:
        data = res.json()
        if data["status"] == "ok":
            air_quality = data["data"]["aqi"]
            #lat = int(data["data"]["city"]["geo"][0])
            #lon = int(data["data"]["city"]["geo"][1])
            air_quality = air_quality
            if log:
                log_queue.put(f"Calidad del aire: {air_quality}")
            return air_quality
        else:
            if log:
                log_queue.put(f"API Error fetching air quality: {data['message']}")
    else:
        if log:
            if res:
                log_queue.put(f"HTTP Error fetching air quality: {res.status_code}")
            else:
                log_queue.put("HTTP Error fetching air quality")
    return None

def GetTemperatureAndHumidity():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m"]
    }
    try:
        res = openmeteo.weather_api(url, params=params)
        if not res:
            if log:
                log_queue.put(f"GetTemperatureAndHumidity Error: 'res' is None")
            return None
        current = res[0].Current()
        if not current:
            if log:
                log_queue.put(f"GetTemperatureAndHumidity Error: 'current' is None")
            return None
        temperature = round(current.Variables(0).Value())
        humidity = round(current.Variables(1).Value())
        temperature = temperature
        humidity = humidity
        if log:
            log_queue.put(f"Temperatura: {str(temperature)} C\nHumedad: {str(humidity)}%")
        return temperature, humidity
    except Exception as e:
        if log:
            log_queue.put(f"GetTemperatureAndHumidity Error: {e}")
    return None

#def fetch():
#    with ThreadPoolExecutor() as executor:
#        future_a = executor.submit(GetAirQuality)
#        future_th = executor.submit(GetTemperatureAndHumidity)
#        air_quality = future_a.result()
#        result_th = future_th.result()
#    if result_th is None:
#        temperature, humidity = None, None
#    else:
#        temperature, humidity = result_th
#    return {
#        "air_quality": air_quality,
#        "temperature": temperature,
#        "humidity": humidity
#    }

def fetch():
    air_quality = GetAirQuality()
    temperature, humidity = GetTemperatureAndHumidity()
    return {
        "air_quality": air_quality,
        "temperature": temperature,
        "humidity": humidity
    }
