"""WeatherLink and Windy API clients."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
import hashlib
import hmac
import logging

from aiohttp import ClientSession

from .const import WEATHERLINK_BASE_URL, WINDY_POINT_FORECAST_URL

_LOGGER = logging.getLogger(__name__)


class WeatherLinkApiClient:
    """API client for WeatherLink v2 station data."""

    def __init__(self, session: ClientSession, api_key: str, api_secret: str) -> None:
        self._session = session
        self._api_key = api_key
        self._api_secret = api_secret

    async def async_get_current_conditions(self, station_id: str) -> dict:
        """Fetch current station observations."""
        timestamp = str(int(datetime.now(tz=UTC).timestamp()))
        params = {"api-key": self._api_key, "t": timestamp}

        signature_payload = "".join(f"{key}{value}" for key, value in sorted(params.items()))
        signature = hmac.new(
            self._api_secret.encode("utf-8"),
            signature_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        params["api-signature"] = signature
        url = f"{WEATHERLINK_BASE_URL}/current/{station_id}"

        async with self._session.get(url, params=params, timeout=20) as response:
            response.raise_for_status()
            payload = await response.json()
            return payload


class WindyPointForecastClient:
    """Client for Windy Point Forecast API v2."""

    def __init__(self, session: ClientSession, api_key: str | None) -> None:
        self._session = session
        self._api_key = api_key

    async def async_get_forecast(self, latitude: float, longitude: float) -> dict | None:
        """Fetch forecast fields from Windy for the configured location."""
        if not self._api_key:
            return None

        headers = {
            "Content-Type": "application/json",
            "x-windy-key": self._api_key,
        }
        body = {
            "lat": latitude,
            "lon": longitude,
            "model": "ecmwf",
            "parameters": ["temp", "wind", "windGust", "precip", "clouds"],
            "levels": ["surface"],
        }

        async with self._session.post(
            WINDY_POINT_FORECAST_URL,
            headers=headers,
            json=body,
            timeout=25,
        ) as response:
            if response.status >= 400:
                body = await response.text()
                _LOGGER.warning("Windy request failed (%s): %s", response.status, body)
                return None
            return await response.json()


def find_value(data: object, keys: tuple[str, ...]) -> float | int | None:
    """Find first value that matches one of the candidate keys in nested payloads."""
    if isinstance(data, list):
        for item in data:
            value = find_value(item, keys)
            if value is not None:
                return value
        return None

    if not isinstance(data, Mapping):
        return None

    for key in keys:
        if key in data and isinstance(data[key], (int, float)):
            return data[key]

    for value in data.values():
        nested = find_value(value, keys)
        if nested is not None:
            return nested

    return None
