from django.shortcuts import render
from decouple import config
import requests


def weather_home(request):

    # TODO: maybe geolocation?
    city = "Gdansk"

    if request.method == "POST":
        city = request.POST['city'].title()

    api_url: str = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}' \
                   f'?unitGroup=metric&include=days%2Ccurrent%2Cevents%2Calerts&key={config("WEATHER_API_KEY")}' \
                   f'&contentType=json'
    weather_data = requests.get(api_url).json()

    context = {
        "name": weather_data['address'],
        "country": weather_data['resolvedAddress'],
        'today': weather_data['days'][0],
        'next_days': weather_data['days'][1:5],
    }

    return render(request, 'app_weather/weather_home.html', context)
