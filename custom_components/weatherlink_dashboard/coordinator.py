"""Coordinator for weather dashboard updates."""

from __future__ import annotations

from datetime import UTC, datetime
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_FORECAST,
    ATTR_STATION_NAME,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_SCAN_INTERVAL,
    CONF_STATION_ID,
    CONF_WINDY_POINT_API_KEY,
    CONF_WEATHERLINK_API_KEY,
    CONF_WEATHERLINK_API_SECRET,
    DOMAIN,
    WINDY_UPDATE_INTERVAL,
)
from .weatherlink_api import WeatherLinkApiClient, WindyPointForecastClient, find_value

_LOGGER = logging.getLogger(__name__)


class WeatherDashboardCoordinator(DataUpdateCoordinator[dict]):
    """Coordinate WeatherLink and Windy data retrieval."""

    def __init__(self, hass: HomeAssistant, config: dict) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=config[CONF_SCAN_INTERVAL],
        )
        self._config = config
        session = async_get_clientsession(hass)
        self._weatherlink = WeatherLinkApiClient(
            session,
            config[CONF_WEATHERLINK_API_KEY],
            config[CONF_WEATHERLINK_API_SECRET],
        )
        self._windy = WindyPointForecastClient(session, config.get(CONF_WINDY_POINT_API_KEY))
        self._forecast_cache: dict | None = None
        self._forecast_last_update: datetime | None = None

    async def _async_update_data(self) -> dict:
        """Fetch latest station and forecast data."""
        try:
            station_payload = await self._weatherlink.async_get_current_conditions(
                self._config[CONF_STATION_ID]
            )
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"Unable to fetch WeatherLink data: {err}") from err

        now = dt_util.utcnow()
        if self._forecast_last_update is None or now - self._forecast_last_update >= WINDY_UPDATE_INTERVAL:
            try:
                self._forecast_cache = await self._windy.async_get_forecast(
                    self._config[CONF_LATITUDE],
                    self._config[CONF_LONGITUDE],
                )
                self._forecast_last_update = now
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("Unable to refresh Windy forecast: %s", err)

        return {
            "station": self._normalize_station(station_payload),
            ATTR_FORECAST: self._normalize_forecast(self._forecast_cache),
        }

    def _normalize_station(self, payload: dict) -> dict:
        """Normalize station payload into expected sensor values (metric units)."""
        temperature_f = find_value(payload, ("temp", "temp_out", "temperature", "temp_in"))
        pressure_inhg = find_value(payload, ("bar_sea_level", "barometer", "bar"))
        wind_mph = find_value(payload, ("wind_speed_avg_last_1_min", "wind_speed", "wind_speed_last"))
        gust_mph = find_value(payload, ("wind_speed_hi_last_10_min", "wind_gust", "wind_gust_last"))
        rain_rate_in_h = find_value(payload, ("rain_rate_last", "rain_rate", "rainfall_rate"))

        station_data = {
            "temperature": self._f_to_c(temperature_f),
            "humidity": find_value(payload, ("hum", "hum_out", "humidity", "hum_in")),
            "wind_speed": self._mph_to_ms(wind_mph),
            "wind_gust": self._mph_to_ms(gust_mph),
            "wind_direction": find_value(payload, ("wind_dir_last", "wind_dir", "wind_direction")),
            "barometric_pressure": self._inhg_to_hpa(pressure_inhg),
            "rain_rate": self._inch_to_mm(rain_rate_in_h),
            "daily_rainfall": self._inch_to_mm(
                find_value(payload, ("rainfall_daily", "rainfall_day", "rain_day"))
            ),
            "storm_rainfall_total": self._inch_to_mm(
                find_value(payload, ("rain_storm", "storm_rain", "rainfall_storm"))
            ),
            "monthly_rainfall": self._inch_to_mm(
                find_value(payload, ("rainfall_monthly", "rain_month", "rainfall_month"))
            ),
            "yearly_rainfall": self._inch_to_mm(
                find_value(payload, ("rainfall_year", "rain_year", "rainfall_yearly"))
            ),
            ATTR_STATION_NAME: "Annerley",
            "last_update_utc": datetime.now(tz=UTC).isoformat(),
        }
        return station_data

    def _normalize_forecast(self, payload: dict | None) -> dict | None:
        """Build summary metrics from Windy forecast payload."""
        if not payload:
            return None

        ts = payload.get("ts", [])
        precip = payload.get("precip", [])
        wind = payload.get("wind", [])
        temperature = payload.get("temp", [])
        clouds = payload.get("clouds", [])

        if not isinstance(ts, list):
            return None

        now_ts = int(datetime.now(tz=UTC).timestamp() * 1000)
        window_end = now_ts + (24 * 60 * 60 * 1000)
        indexes = [i for i, value in enumerate(ts) if now_ts <= value <= window_end]

        if not indexes:
            return None

        total_rain_24h = sum(float(precip[i]) for i in indexes if i < len(precip))
        max_wind_24h = max((float(wind[i]) for i in indexes if i < len(wind)), default=0)
        temp_values = [float(temperature[i]) for i in indexes if i < len(temperature)]

        temp_trend = None
        if len(temp_values) >= 2:
            delta = temp_values[-1] - temp_values[0]
            temp_trend = "rising" if delta > 0.5 else "falling" if delta < -0.5 else "steady"

        cloud_values = [float(clouds[i]) for i in indexes if i < len(clouds)]

        return {
            "next_24h_rain_mm": round(total_rain_24h, 1),
            "next_24h_max_wind_ms": round(max_wind_24h, 1),
            "temperature_trend": temp_trend,
            "average_cloud_cover_pct": round(sum(cloud_values) / len(cloud_values), 1)
            if cloud_values
            else None,
        }

    @staticmethod
    def _f_to_c(value: float | int | None) -> float | None:
        if value is None:
            return None
        return round((float(value) - 32.0) * 5.0 / 9.0, 1)

    @staticmethod
    def _mph_to_ms(value: float | int | None) -> float | None:
        if value is None:
            return None
        return round(float(value) * 0.44704, 1)

    @staticmethod
    def _inch_to_mm(value: float | int | None) -> float | None:
        if value is None:
            return None
        return round(float(value) * 25.4, 1)

    @staticmethod
    def _inhg_to_hpa(value: float | int | None) -> float | None:
        if value is None:
            return None
        return round(float(value) * 33.8639, 1)
