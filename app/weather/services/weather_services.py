import logging
import requests
from typing import Optional

from django.conf import settings
from django.db import connection
from django.core.cache import cache

logger = logging.getLogger("weather")


class WeatherApiService:

    UNIT_MAP = {
        "celsius": "metric",
        "fahrenheit": "imperial",
    }

    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_BASE_URL

    def get_weather(self, city: str, units: str) -> Optional[dict]:

        logger.info(f"api_request_started {city=} {units=}")

        params = {
            "q": city,
            "appid": self.api_key,
            "units": self.UNIT_MAP[units],
        }

        try:
            response = requests.get(
                url=self.base_url,
                params=params,
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"api_request_success {city=} {response.status_code=}")
            return self._normalize(data)

        except requests.RequestException as error:
            logger.error(f"api_request_failed {city=} {error.response.status_code=}")
            return None

    def _normalize(self, data: dict) -> dict:

        current = data["list"][0]

        return {
            "city": data["city"]["name"],
            "temperature": current["main"]["temp"],
            "feels_like": current["main"]["feels_like"],
            "description": current["weather"][0]["description"],
            "humidity": current["main"]["humidity"],
            "wind_speed": current["wind"]["speed"],
        }


class WeatherCacheService:

    def _key(self, city: str) -> str:
        city_key = city.strip().title().replace(" ", "_")
        return f"weather:{city_key}"

    def get(self, city: str):
        key = self._key(city)
        try:
            cached = cache.get(key)
        except Exception as e:
            logger.warning(f"cache_get_failed city={city} error={e}")
            return None
        if cached is not None:
            logger.info(f"cache_hit city={city}")
            return cached
        logger.info(f"cache_miss city={city}")
        return None

    def set(self, city: str, units: str, data: dict):
        key = self._key(city)
        try:
            cache.set(key, data)
        except Exception as e:
            logger.warning(f"cache_set_failed city={city} error={e}")
            return
        logger.info(f"cache_saved city={city} units={units}")


class WeatherService:

    def __init__(self):
        self.cache_service = WeatherCacheService()
        self.api_service = WeatherApiService()

    def _convert(self, data: dict, to_units: str):
        from_units = data["units"]

        if from_units == to_units:
            return data

        if from_units == "celsius" and to_units == "fahrenheit":
            data["temperature"] = data["temperature"] * 9 / 5 + 32
            data["feels_like"] = data["feels_like"] * 9 / 5 + 32
            data["units"] = "fahrenheit"

        elif from_units == "fahrenheit" and to_units == "celsius":
            data["temperature"] = (data["temperature"] - 32) * 5 / 9
            data["feels_like"] = (data["feels_like"] - 32) * 5 / 9
            data["units"] = "celsius"

        return data

    def get_weather(self, city: str, units: str):
        city = city.strip().title()
        units = units.strip().lower()
        cached_data = self.cache_service.get(city=city)

        if cached_data is not None:
            cached_data["from_cache"] = True
            cached_data = self._convert(data=cached_data, to_units=units)
            return cached_data

        weather_data = self.api_service.get_weather(city=city, units=units)
        if not weather_data:
            return None
        weather_data["from_cache"] = False
        weather_data["units"] = units
        self.cache_service.set(city=city, units=units, data=weather_data)
        return weather_data