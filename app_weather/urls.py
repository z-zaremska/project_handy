from django.urls import path
from app_weather import views

app_name = 'app_weather'

urlpatterns = [
    # App main page
    path('', views.weather_home, name='weather_home'),
]
