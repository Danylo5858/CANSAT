import requests

url = "https://api.waqi.info/feed/@6779/?token=db94e4c768d260335021f2dbc8dfc088345d6bab"
url2 = "https://api.thingspeak.com/update?api_key=BTCDYRXPGC0PZOWK&field1="

res = requests.get(url)

if res.status_code == 200:
    data = res.json()
    air = data["data"]["aqi"]
    print("Calidad del aire:", air)
    res2 = requests.get(url2 + str(air))
    print(res.status_code)
else:
    print("Error:", res.status_code)
