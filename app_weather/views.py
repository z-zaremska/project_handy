from django.shortcuts import render
from decouple import config
import urllib.request
import json


def weather_home(request):

    city = "Gdansk"

    if request.method == "POST":
        city = request.POST['city'].title()

    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric$appid={config('WEATHER_API_KEY')}"
    source = urllib.request.urlopen(api_url).read()
    weather_data = json.loads(source)

    context = {
        "name": weather_data['name'],
        "country_code": weather_data['sys']['country'],
        "sunrise": weather_data['sys']['sunrise'],
        "sunset": weather_data['sys']['sunset'],
        "temp": weather_data['main']['temp'],
        "temp_min": weather_data['main']['temp_min'],
        "temp_max": weather_data['main']['temp_max'],
        "pressure": weather_data['main']['pressure'],
        "humidity": weather_data['main']['humidity'],
        "main": weather_data['weather'][0]['main'],
        "description": weather_data['weather'][0]['description'],
        "visibility": weather_data['visibility'],
        "wind_speed": weather_data['wind']['speed'],
        "clouds": weather_data['clouds']['all'],
    }

    return render(request, 'app_weather/weather_home.html', context)
