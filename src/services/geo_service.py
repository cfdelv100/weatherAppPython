import requests

from src import config


class GeoService:
    def __init__(self, api_key: str = config.WEATHER_API_KEY, base_url: str = config.WEATHER_GEO_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url

    def geocode_city(self, city: str) -> dict | None:
        response = requests.get(
            self.base_url,
            params={"q": city, "limit": 1, "appid": self.api_key},
            timeout=15,
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            return None
        return results[0]
