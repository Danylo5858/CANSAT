import requests
import openmeteo_requests

openmeteo = openmeteo_requests.Client()

def GetAirQuality():
    global air_quality, latitude, longitude
    url = "https://api.waqi.info/feed/@6779/?token=db94e4c768d260335021f2dbc8dfc088345d6bab"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        air_quality = data["data"]["aqi"]
        latitude = int(data["data"]["city"]["geo"][0])
        longitude = int(data["data"]["city"]["geo"][1])
        print("Calidad del aire:", air_quality)
    else:
        print("Error fetching air quality:", res.status_code)

def GetTemperatureAndHumidity():
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
    print("Temperatura:", str(temperature) + " C")
    print("Humedad:", str(humidity) + "%")

def UpdateGraph():
    url = f"https://api.thingspeak.com/update?api_key=BTCDYRXPGC0PZOWK&field1={air_quality}&field2={temperature}&field3={humidity}"
    res = requests.get(url)
    if res.status_code == 200:
        print("Success")
    else:
        print("Error updating data:", res.status_code)

GetAirQuality()
GetTemperatureAndHumidity()
UpdateGraph()
