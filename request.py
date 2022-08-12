from geopy.geocoders import Nominatim
from config import USER_AGENT
import requests
import datetime


geolocation = Nominatim(user_agent=USER_AGENT)


def get_location(city):
    location = geolocation.geocode(city)
    if location is not None:
        lat = location.latitude
        lon = location.longitude
        return [lat, lon]
    return None


def get_weather(latitude: float, longitude: float, api_key: str):
    url = 'https://api.openweathermap.org/data/2.5/weather?units=metric&lang=ru&appid=' + \
          f'{api_key}&lat={latitude}&lon={longitude}'
    response = requests.get(url=url)
    data = response.json()
    temp = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    discription = data['weather'][0]['description']

    sunrise_time = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
    sunset_time = datetime.datetime.fromtimestamp(data['sys']['sunset'])
    day_lenght = str(sunset_time - sunrise_time)[:5]

    sunrise_time = '{:02d}:{:02d}'.format(sunrise_time.hour, sunrise_time.minute)
    sunset_time = '{:02d}:{:02d}'.format(sunset_time.hour, sunset_time.minute)

    return f"Сегодня {discription}.\nТемпература на день составляет: {int(temp)} С\n" \
           f"Влажность воздуха составляет: {humidity}%\nСкорость ветра: {wind_speed} м/с\n" \
           f"Время восхода солнца: {sunrise_time}\nВремя заката: {sunset_time}\nПродолжительность дня: {day_lenght}"
