import json
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import urlopen


class WeatherServiceError(Exception):
    pass


class WeatherService:
    def __init__(self, led_controller, location=None):
        self.led_controller = led_controller
        self.location = location.strip() if location else ""
        self._weather = None

    @property
    def weather(self):
        return self._weather

    def refresh(self, location=None):
        if location is not None:
            self.location = location.strip()
        if not self.location:
            raise WeatherServiceError("Location is required")

        try:
            coordinates = self._geocode(self.location)
            data = self._fetch_weather(coordinates)
        except Exception as error:
            raise WeatherServiceError(f"Weather service unavailable: {error}") from error

        result = self._to_weather_result(coordinates, data)
        self._weather = result
        self.led_controller.set_weather(result["weather"])
        return result

    def _geocode(self, location):
        query = urlencode({"name": location, "count": 1, "language": "en", "format": "json"})
        payload = self._get_json(f"https://geocoding-api.open-meteo.com/v1/search?{query}")
        results = payload.get("results") or []
        if not results:
            raise WeatherServiceError(f"Location not found: {location}")
        result = results[0]
        return {
            "name": result.get("name", location),
            "latitude": result["latitude"],
            "longitude": result["longitude"],
        }

    def _fetch_weather(self, coordinates):
        query = urlencode({
            "latitude": coordinates["latitude"],
            "longitude": coordinates["longitude"],
            "current": "temperature_2m,rain,precipitation,wind_speed_10m,weather_code",
            "timezone": "auto",
        })
        return self._get_json(f"https://api.open-meteo.com/v1/forecast?{query}")

    @staticmethod
    def _get_json(url):
        with urlopen(url, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))

    @staticmethod
    def _to_weather_result(coordinates, payload):
        current = payload["current"]
        return {
            "location": coordinates["name"],
            "temperature": current.get("temperature_2m"),
            "rain": current.get("rain", 0),
            "precipitation": current.get("precipitation", 0),
            "weather": classify_weather(current.get("weather_code")),
            "wind_speed": current.get("wind_speed_10m"),
            "time": current.get("time") or datetime.now(timezone.utc).isoformat(),
        }


def classify_weather(weather_code):
    if weather_code in {0, 1}:
        return "NANG"
    if weather_code in {2, 3, 45, 48}:
        return "CO MAY"
    if weather_code is not None and 51 <= weather_code <= 99:
        return "MUA"
    return "KHONG XAC DINH"
