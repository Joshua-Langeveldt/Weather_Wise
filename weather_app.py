from flask import Flask, send_from_directory, request, jsonify
import requests
import os

app = Flask(__name__)

API_key = "59e5d55ce31b992f2a83f5ddd0a1b7be"

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_key}"
    res = requests.get(url)

    if res.status_code == 404:
        return None

    weather = res.json()
    icon_id = weather['weather'][0]['icon']
    temperature = weather['main']['temp'] - 273.15
    description = weather['weather'][0]['description']
    wind_speed = weather['wind']['speed']
    humidity = weather['main']['humidity']
    city = weather['name']
    country = weather['sys']['country']
    lat = weather['coord']['lat']
    lon = weather['coord']['lon']

    icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
    return (icon_url, temperature, description, wind_speed, humidity, city, country, lat, lon)

def get_forecast(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_key}"
    res = requests.get(url)

    if res.status_code != 200:
        return None

    forecast = res.json().get('list', [])[:4]
    if not forecast:
        return None

    forecast_data = []
    for item in forecast:
        temp = item['main']['temp'] - 273.15
        desc = item['weather'][0]['description']
        icon_id = item['weather'][0]['icon']
        icon_url = f"https://openweathermap.org/img/wn/{icon_id}@2x.png"
        forecast_data.append((temp, desc.capitalize(), icon_url))
    return forecast_data

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/weather', methods=['POST'])
def weather():
    city = request.form['city']
    data = get_weather(city)
    if data is None:
        return jsonify({"error": "City not found"}), 404

    icon_url, temperature, description, wind_speed, humidity, city, country, lat, lon = data

    forecast = get_forecast(lat, lon)
    if forecast is None:
        return jsonify({
            "error": "Forecast data unavailable",
            "current": (icon_url, temperature, description, wind_speed, humidity, city, country)
        })

    return jsonify({
        "current": (icon_url, temperature, description, wind_speed, humidity, city, country),
        "forecast": forecast
    })

if __name__ == '__main__':
    app.run(debug=True)
