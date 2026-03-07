"""Sensor platform for WeatherLink Dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import voluptuous as vol

from homeassistant.components.sensor import (
    PLATFORM_SCHEMA,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_SCAN_INTERVAL,
    DEGREE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_FORECAST,
    ATTR_STATION_NAME,
    CONF_STATION_ID,
    CONF_WINDY_POINT_API_KEY,
    CONF_WEATHERLINK_API_KEY,
    CONF_WEATHERLINK_API_SECRET,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .coordinator import WeatherDashboardCoordinator

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_STATION_ID): cv.string,
        vol.Required(CONF_WEATHERLINK_API_KEY): cv.string,
        vol.Required(CONF_WEATHERLINK_API_SECRET): cv.string,
        vol.Required(CONF_LATITUDE): cv.latitude,
        vol.Required(CONF_LONGITUDE): cv.longitude,
        vol.Optional(CONF_WINDY_POINT_API_KEY): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    }
)


@dataclass(frozen=True)
class WeatherSensorDescription:
    """Entity description for station and forecast metrics."""

    key: str
    name: str
    native_unit_of_measurement: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = SensorStateClass.MEASUREMENT
    icon: str | None = None


LIVE_SENSOR_DESCRIPTIONS: tuple[WeatherSensorDescription, ...] = (
    WeatherSensorDescription("temperature", "Annerley Temperature", UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE),
    WeatherSensorDescription("humidity", "Annerley Humidity", "%", SensorDeviceClass.HUMIDITY),
    WeatherSensorDescription("wind_speed", "Annerley Wind Speed", UnitOfSpeed.METERS_PER_SECOND, SensorDeviceClass.WIND_SPEED),
    WeatherSensorDescription("wind_gust", "Annerley Wind Gust", UnitOfSpeed.METERS_PER_SECOND, SensorDeviceClass.WIND_SPEED),
    WeatherSensorDescription("wind_direction", "Annerley Wind Direction", DEGREE, icon="mdi:compass"),
    WeatherSensorDescription(
        "barometric_pressure",
        "Annerley Barometric Pressure",
        UnitOfPressure.HPA,
        SensorDeviceClass.ATMOSPHERIC_PRESSURE,
    ),
    WeatherSensorDescription(
        "rain_rate",
        "Annerley Rain Rate",
        "mm/h",
        SensorDeviceClass.PRECIPITATION_INTENSITY,
    ),
    WeatherSensorDescription("daily_rainfall", "Annerley Daily Rainfall", "mm", SensorDeviceClass.PRECIPITATION),
    WeatherSensorDescription(
        "storm_rainfall_total", "Annerley Storm Rainfall Total", "mm", SensorDeviceClass.PRECIPITATION
    ),
    WeatherSensorDescription("monthly_rainfall", "Annerley Monthly Rainfall", "mm", SensorDeviceClass.PRECIPITATION),
    WeatherSensorDescription("yearly_rainfall", "Annerley Yearly Rainfall", "mm", SensorDeviceClass.PRECIPITATION),
)

FORECAST_SENSOR_DESCRIPTIONS: tuple[WeatherSensorDescription, ...] = (
    WeatherSensorDescription("next_24h_rain_mm", "Annerley Forecast Rain (24h)", "mm", SensorDeviceClass.PRECIPITATION),
    WeatherSensorDescription(
        "next_24h_max_wind_ms",
        "Annerley Forecast Max Wind (24h)",
        UnitOfSpeed.METERS_PER_SECOND,
        SensorDeviceClass.WIND_SPEED,
    ),
    WeatherSensorDescription("temperature_trend", "Annerley Temperature Trend", icon="mdi:thermometer-chevron-up"),
    WeatherSensorDescription("average_cloud_cover_pct", "Annerley Cloud Cover (24h Avg)", "%", icon="mdi:weather-cloudy"),
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict,
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict | None = None,
) -> None:
    """Set up WeatherLink dashboard sensors from YAML config."""
    coordinator = WeatherDashboardCoordinator(hass, dict(config))
    await coordinator.async_refresh()

    entities: list[SensorEntity] = [
        WeatherDashboardLiveSensor(coordinator, description)
        for description in LIVE_SENSOR_DESCRIPTIONS
    ]
    entities.extend(
        WeatherDashboardForecastSensor(coordinator, description)
        for description in FORECAST_SENSOR_DESCRIPTIONS
    )
    entities.append(WeatherDashboardMetadataSensor(coordinator))

    async_add_entities(entities)


class WeatherDashboardBaseSensor(CoordinatorEntity[WeatherDashboardCoordinator], SensorEntity):
    """Base sensor for station/forecast values."""

    _attr_has_entity_name = False

    def __init__(self, coordinator: WeatherDashboardCoordinator, description: WeatherSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_icon = description.icon
        self._attr_unique_id = f"{DOMAIN}_{description.key}"

    @property
    def available(self) -> bool:
        """Return availability based on coordinator state."""
        return super().available and self.coordinator.last_update_success

    @property
    def device_info(self) -> dict[str, Any]:
        """Return station device metadata."""
        station_name = self.coordinator.data.get("station", {}).get(ATTR_STATION_NAME, "Annerley")
        return {
            "identifiers": {(DOMAIN, "annerley_station")},
            "name": station_name,
            "manufacturer": "Davis Instruments",
            "model": "Vantage Vue",
        }


class WeatherDashboardLiveSensor(WeatherDashboardBaseSensor):
    """Live WeatherLink observation sensor."""

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get("station", {}).get(self.entity_description.key)


class WeatherDashboardForecastSensor(WeatherDashboardBaseSensor):
    """Windy forecast summary sensor."""

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get(ATTR_FORECAST, {}).get(self.entity_description.key)


class WeatherDashboardMetadataSensor(CoordinatorEntity[WeatherDashboardCoordinator], SensorEntity):
    """Diagnostic sensor for timestamp of latest WeatherLink update."""

    _attr_has_entity_name = False
    _attr_name = "Annerley WeatherLink Last Update"
    _attr_icon = "mdi:update"
    _attr_unique_id = f"{DOMAIN}_last_update"

    @property
    def available(self) -> bool:
        return super().available and self.coordinator.last_update_success

    @property
    def native_value(self) -> Any:
        return self.coordinator.data.get("station", {}).get("last_update_utc")

    @property
    def device_info(self) -> dict[str, Any]:
        return {
            "identifiers": {(DOMAIN, "annerley_station")},
            "name": self.coordinator.data.get("station", {}).get(ATTR_STATION_NAME, "Annerley"),
            "manufacturer": "Davis Instruments",
            "model": "Vantage Vue",
        }
