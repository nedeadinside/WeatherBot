from config import WEATHER_API_KEY, USER_AGENT
from geopy.geocoders import Nominatim
import requests

geolocation = Nominatim(user_agent=USER_AGENT)


def get_location(city):
    location = geolocation.geocode(city)
    if location is not None:
        lat = location.latitude
        lon = location.longitude
        return [lat, lon]
    return None


def url_request(latitude, longitude):
    url = f'https://api.openweathermap.org/data/3.0/onecall?lat={latitude}&lon={longitude}&exclude=daily&appid={WEATHER_API_KEY}'
    response = requests.get(url=url)
    return response.json()
