from io import BytesIO

import requests

from src import config


class WeatherService:
    def __init__(self, api_key: str = config.WEATHER_API_KEY, base_url: str = config.WEATHER_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url

    def get_weather(self, city: str) -> dict:
        response = requests.get(
            self.base_url,
            params={"q": city, "appid": self.api_key},
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def get_icon_bytes(self, icon_code: str) -> BytesIO | None:
        response = requests.get(
            f"{config.WEATHER_ICON_BASE_URL}/{icon_code}@2x.png",
            timeout=15,
        )
        if response.status_code != 200:
            return None
        return BytesIO(response.content)
