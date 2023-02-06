from django.shortcuts import render


def weather_home(request):
    return render(request, 'app_weather/weather_home.html')
