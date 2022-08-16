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


def get_weather(latitude, longitude, api_key: str):
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
    return f"Сейчас {discription}.\nТемпература составляет: {int(temp)} °C\n" \
           f"Влажность воздуха составляет: {humidity}%\nСкорость ветра: {wind_speed} м/с\n" \
           f"Время восхода солнца: {sunrise_time}\nВремя заката: {sunset_time}\nПродолжительность дня: {day_lenght}"


def get_forecast(latitude, longitude, api_key: str):
    date_now = str(datetime.datetime.now())[:10]

    response = requests.get(url='https://api.openweathermap.org/data/2.5/forecast?units=metric&lang=ru' +
                                f'&appid={api_key}&lat={latitude}&lon={longitude}')
    data = response.json()
    lst = data['list']
    today_forecast = [i for i in lst if i['dt_txt'][:10] == date_now]
    len_forecast = len(today_forecast)

    avg_temp = 0
    avg_humidity = 0
    avg_wind = 0
    weather = 'Прогноз по времени. Помни, что все время указывается по МСК\n\n'

    for i in today_forecast:
        avg_temp += i['main']['temp']
        avg_humidity += i['main']['humidity']
        avg_wind += i['wind']['speed']

        hours = int(i['dt_txt'][11:13])
        minutes = int(i['dt_txt'][14:16])
        time = datetime.datetime(hour=hours, minute=minutes, day=1, month=1, year=2022)
        time += datetime.timedelta(hours=3)
        time = str(time)

        weather += f'{str(time[11:16])} - {i["weather"][0]["description"]}\n' \
                       f'Температура: {i["main"]["temp"]} °C\n' \
                       f'Влажность: {i["main"]["humidity"]}%\n' \
                       f'Скорость ветра: {i["wind"]["speed"]} м/c\n\n'

    avg_temp = round(avg_temp / len_forecast, 1)
    avg_humidity = round(avg_humidity / len_forecast, 1)
    avg_wind = round(avg_wind / len_forecast, 1)

    sunrise_time = datetime.datetime.fromtimestamp(data['city']['sunrise'])
    sunset_time = datetime.datetime.fromtimestamp(data['city']['sunset'])

    day_length = str(sunset_time - sunrise_time)[:5]
    sunrise_time = '{:02d}:{:02d}'.format(sunrise_time.hour, sunrise_time.minute)
    sunset_time = '{:02d}:{:02d}'.format(sunset_time.hour, sunset_time.minute)

    return weather + f'Средняя температура: {avg_temp} °C\n' \
                     f'Средняя влажность: {avg_humidity}%\n' \
                     f'Средняя скорость ветра: {avg_wind} м/c\n' \
                     f'Восход солнца: {sunrise_time}\n' \
                     f'Заход солнца: {sunset_time}\n' \
                     f'Продолжительность дня: {day_length}'
