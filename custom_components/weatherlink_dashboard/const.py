"""Constants for the WeatherLink dashboard integration."""

from datetime import timedelta

DOMAIN = "weatherlink_dashboard"
PLATFORMS = ["sensor"]

CONF_STATION_ID = "station_id"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"
CONF_WEATHERLINK_API_KEY = "weatherlink_api_key"
CONF_WEATHERLINK_API_SECRET = "weatherlink_api_secret"
CONF_WINDY_POINT_API_KEY = "windy_point_api_key"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_SCAN_INTERVAL = timedelta(seconds=60)
WINDY_UPDATE_INTERVAL = timedelta(minutes=30)

WEATHERLINK_BASE_URL = "https://api.weatherlink.com/v2"
WINDY_POINT_FORECAST_URL = "https://api.windy.com/api/point-forecast/v2"

ATTR_FORECAST = "forecast"
ATTR_STATION_NAME = "station_name"
