from django.shortcuts import render
from django.contrib import messages
from decouple import config
import requests
from app_weather.weather_icon_translation import weather_icons


def weather_home(request):

    # TODO: maybe geolocation?
    city = "Gdansk"

    if request.method == "POST":
        city = request.POST['city'].title()

    api_url: str = f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}' \
                   f'?unitGroup=metric&include=days%2Ccurrent%2Cevents%2Calerts&key={config("WEATHER_API_KEY")}' \
                   f'&contentType=json'
    try:
        weather_data = requests.get(api_url).json()
        # adjust API icons to layout icons
        for day in weather_data['days']:
            if day['icon'] in weather_icons.keys():
                key = day['icon']
                day['icon'] = weather_icons[key]

        context = {
            "name": weather_data['address'],
            "country": weather_data['resolvedAddress'],
            'today': weather_data['days'][0],
            'next_days': weather_data['days'][1:5]
        }
        return render(request, 'app_weather/weather_home.html', context)
    except ValueError:
        no_such_city = f'Sorry, we know nothing about "{city}" city'
        return render(request, 'app_weather/weather_home.html', {'no_such_city': no_such_city})
