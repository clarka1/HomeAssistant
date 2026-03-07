# HomeAssistant Dashboards

A collection of [Home Assistant](https://www.home-assistant.io/) Lovelace dashboards, themes, and custom card configurations.

## Repository Structure

```
.
├── dashboards/                              # Lovelace dashboard YAML files
│   ├── home.yaml                            # Main overview dashboard
│   ├── energy.yaml                          # Energy monitoring dashboard
│   └── weather_dashboard.yaml               # Weather station dashboard (Live + Forecast)
├── themes/                                  # Custom UI themes
│   └── default.yaml                         # Default theme
├── custom_cards/                            # Custom Lovelace card resources
└── custom_components/weatherlink_dashboard/ # Custom WeatherLink sensor integration
```

## Weather Dashboard (Annerley)

The weather solution in this repository provides:

- WeatherLink API v2 live station polling (60-second interval),
- Home Assistant sensors for all requested live metrics,
- Windy point-forecast summary sensors (rainfall/wind/temperature trend/cloud cover),
- a two-view Lovelace dashboard designed for tablet use.

### 1) Copy files into Home Assistant config

From this repository, copy:

- `custom_components/weatherlink_dashboard/` → `/config/custom_components/weatherlink_dashboard/`
- `dashboards/weather_dashboard.yaml` → `/config/dashboards/weather_dashboard.yaml`

### 2) Configure secrets

In `/config/secrets.yaml` define:

```yaml
weatherlink_api_key: YOUR_WEATHERLINK_API_KEY
weatherlink_api_secret: YOUR_WEATHERLINK_API_SECRET
windy_map_api_key: YOUR_WINDY_MAP_API_KEY
windy_point_api_key: YOUR_WINDY_POINT_API_KEY
```

### 3) Configure sensors in `configuration.yaml`

```yaml
sensor:
  - platform: weatherlink_dashboard
    station_id: 73624e8add9f4437b9e61c613188df34
    latitude: -27.51638
    longitude: 153.02674
    weatherlink_api_key: !secret weatherlink_api_key
    weatherlink_api_secret: !secret weatherlink_api_secret
    windy_point_api_key: !secret windy_point_api_key
    scan_interval: "00:01:00"
```

### 4) Register the dashboard in Lovelace

```yaml
lovelace:
  mode: yaml
  dashboards:
    lovelace-weather:
      mode: yaml
      filename: dashboards/weather_dashboard.yaml
      title: Weather
      icon: mdi:weather-partly-rainy
      show_in_sidebar: true
```

### 5) Restart Home Assistant

Restart from **Settings → System → Restart**.

### 6) Verify entities and dashboard

Expected entity IDs:

- `sensor.annerley_temperature`
- `sensor.annerley_humidity`
- `sensor.annerley_wind_speed`
- `sensor.annerley_wind_gust`
- `sensor.annerley_wind_direction`
- `sensor.annerley_barometric_pressure`
- `sensor.annerley_rain_rate`
- `sensor.annerley_daily_rainfall`
- `sensor.annerley_storm_rainfall_total`
- `sensor.annerley_monthly_rainfall`
- `sensor.annerley_yearly_rainfall`
- `sensor.annerley_forecast_rain_24h`
- `sensor.annerley_forecast_max_wind_24h`
- `sensor.annerley_temperature_trend`
- `sensor.annerley_cloud_cover_24h_avg`

Open the **Weather** dashboard on iPad from the left sidebar.

## Dashboard features

### Live Weather view
- live station entity list (all required sensors),
- 24-hour history graph for temperature, wind speed, rain rate, pressure,
- map centered on local area,
- Windy radar + satellite embeds with in-map layer controls (`menu=true`).

### Forecast view
- forecast summary entity list,
- Windy wind map,
- Windy precipitation map,
- Windy cloud-layer map.

## Manual verification checklist

1. Check Home Assistant logs for `weatherlink_dashboard` startup errors.
2. Confirm all `sensor.annerley_*` entities are created.
3. Wait 2–3 minutes and verify the live sensors update.
4. Check forecast sensors update (Windy refresh is less frequent).
5. Open dashboard on iPad and confirm maps render and can be panned/zoomed.

## Themes and custom cards

### Adding Themes

1. Copy YAML files from `themes/` to your Home Assistant `themes/` directory.
2. Add this to `configuration.yaml`:

```yaml
frontend:
  themes: !include_dir_merge_named themes/
```

3. Restart Home Assistant and select your theme via **Profile → Theme**.

### Custom Cards

See [`custom_cards/README.md`](custom_cards/README.md) for instructions on adding custom Lovelace cards.
