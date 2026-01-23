import httpx
from datetime import datetime
import logging

from app.config import get_settings
from app.models.schemas import WeatherStatus, WeatherForecast, StatusLevel
from app.services.cache import cache_service
from app.utils.runtime_config import get_service_enabled

logger = logging.getLogger(__name__)

CACHE_KEY = "weather_status"

# WMO Weather interpretation codes mapping
WMO_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌧️"),
    53: ("Moderate drizzle", "🌧️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Light freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Light freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snow fall", "🌨️"),
    73: ("Moderate snow fall", "🌨️"),
    75: ("Heavy snow fall", "🌨️"),
    77: ("Snow grains", "🌨️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌦️"),
    82: ("Violent rain showers", "🌦️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "🌨️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


def get_weather_description(code: int) -> tuple:
    """Get weather description and icon from WMO code."""
    return WMO_CODES.get(code, ("Unknown", "❓"))


class WeatherService:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"

    async def get_status(self, use_cache: bool = True) -> WeatherStatus:
        """Get weather forecast from Open-Meteo API."""
        # Check if service is disabled (from runtime config)
        if not get_service_enabled("weather"):
            return WeatherStatus(
                status=StatusLevel.UNKNOWN,
                error_message="Service disabled",
                last_updated=datetime.now(),
            )

        if use_cache:
            cached = await cache_service.get(CACHE_KEY)
            if cached:
                return cached

        settings = get_settings()

        if settings.weather_latitude == 0.0 and settings.weather_longitude == 0.0:
            return WeatherStatus(
                status=StatusLevel.UNKNOWN,
                error_message="Weather location not configured",
                last_updated=datetime.now(),
            )

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {
                    "latitude": settings.weather_latitude,
                    "longitude": settings.weather_longitude,
                    "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                    "current_weather": "true",
                    "temperature_unit": "fahrenheit",
                    "timezone": "auto",
                    "forecast_days": 2,
                }

                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                # Current weather
                current = data.get("current_weather", {})
                current_temp = current.get("temperature", 0)
                current_code = current.get("weathercode", 0)
                current_desc, current_icon = get_weather_description(current_code)

                # Daily forecasts
                daily = data.get("daily", {})
                daily_max = daily.get("temperature_2m_max", [0, 0])
                daily_codes = daily.get("weathercode", [0, 0])

                # Today's forecast
                today_desc, today_icon = get_weather_description(daily_codes[0] if daily_codes else 0)
                today = WeatherForecast(
                    temperature=round(current_temp),
                    description=current_desc,
                    icon=current_icon,
                )

                # Tomorrow's forecast
                tomorrow_desc, tomorrow_icon = get_weather_description(daily_codes[1] if len(daily_codes) > 1 else 0)
                tomorrow = WeatherForecast(
                    temperature=round(daily_max[1] if len(daily_max) > 1 else 0),
                    description=tomorrow_desc,
                    icon=tomorrow_icon,
                )

                result = WeatherStatus(
                    status=StatusLevel.HEALTHY,
                    today=today,
                    tomorrow=tomorrow,
                    last_updated=datetime.now(),
                )

                await cache_service.set(CACHE_KEY, result)
                return result

        except Exception as e:
            logger.error(f"Weather error: {e}")
            return WeatherStatus(
                status=StatusLevel.ERROR,
                error_message=str(e),
                last_updated=datetime.now(),
            )


weather_service = WeatherService()
