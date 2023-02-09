from django.shortcuts import render
from decouple import config
import urllib.request
import json


def weather_home(request):

    # TODO: maybe geolocation?
    city = "Krakow"

    if request.method == "POST":
        city = request.POST['city'].title()

    api_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&cnt=5&appid={config("WEATHER_API_KEY")}&units=metric&lang=en'
    source = urllib.request.urlopen(api_url).read()
    weather_data = json.loads(source)

    context = {
        "name": weather_data['city']['name'],
        "country_code": weather_data['city']['country'],
        "sunrise": weather_data['city']['sunrise'],
        "sunset": weather_data['city']['sunset'],
        'today_forecast': weather_data['list'][0],
        'next_days_forecast': weather_data['list'][1:],
    }

    return render(request, 'app_weather/weather_home.html', context)
