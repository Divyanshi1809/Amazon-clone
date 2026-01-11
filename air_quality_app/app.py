import requests

API_KEY = "6e6cade4627918fdc36db4015331c54e"  # Replace with your real API key
city = "delhi"

url = f"https://api.waqi.info/feed/{city}/?token={API_KEY}"
response = requests.get(url)

data = response.json()  # <-- This is JSON
print("City:", data["data"]["city"]["name"])
print("AQI:", data["data"]["aqi"])
print("PM2.5:", data["data"]["iaqi"]["pm25"]["v"])


