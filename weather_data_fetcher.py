import requests

url = "https://api.waqi.info/feed/@6753/?token=db94e4c768d260335021f2dbc8dfc088345d6bab"

res = requests.get(url)

if res.status_code == 200:
    data = res.json()
    print("Calidad del aire:", data["data"]["aqi"])
else:
    print("Error:", res.status_code)
