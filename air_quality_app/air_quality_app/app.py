from flask import Flask, render_template, request
import requests

app = Flask(__name__)

WEATHER_API_KEY = "6e6cade4627918fdc36db4015331c54e"

def get_coordinates(city):
    url = f"https://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={WEATHER_API_KEY}"
    response = requests.get(url)
    print("Geo API response:", response.text)  # Debug
    
    if response.status_code == 200:
        data = response.json()
        if data:  # check if list is not empty
            return data[0]['lat'], data[0]['lon']
    return None, None



def get_aqi_data(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
    response = requests.get(url)
    print("AQI API response:", response.text)  # 🔍 Debug
    if response.status_code == 200:
        data = response.json()
        aqi = data['list'][0]['main']['aqi']
        components = data['list'][0]['components']
        return {
            'aqi': aqi,
            'aqi_label': classify_aqi(aqi),
            'components': components
        }
    return {'error': "Failed to fetch AQI data."}

def classify_aqi(aqi):
    labels = {
        1: "Good 😊",
        2: "Fair 🙂",
        3: "Moderate 😐",
        4: "Poor 😷",
        5: "Very Poor ☠️"
    }
    return labels.get(aqi, "Unknown")

@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}
    if request.method == 'POST':
        city = request.form['city']
        lat, lon = get_coordinates(city)
        if lat and lon:
            result = get_aqi_data(lat, lon)
            result['city'] = city.title()
        else:
            result = {'error': f"Could not find coordinates for '{city}'."}
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
