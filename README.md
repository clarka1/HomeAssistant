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
└── custom_components/weatherlink_dashboard/ # Legacy custom WeatherLink sensor integration
```

## Weather Dashboard (Annerley)

The weather dashboard is now wired to the **existing Home Assistant WeatherLink integration entities** already created in your instance.

This avoids failures from non-existent `sensor.annerley_*` entities and keeps the dashboard compatible with an integration that is already working in production.

### 1) Copy files into Home Assistant config

From this repository, copy:

- `dashboards/weather_dashboard.yaml` → `/config/dashboards/weather_dashboard.yaml`

### 2) Register the dashboard in Lovelace

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

### 3) Restart or reload Lovelace dashboards

Apply from **Settings → Dashboards** (reload YAML dashboards) or restart Home Assistant.

### 4) Verify entities and dashboard

Current expected WeatherLink entity IDs (observed in runtime):

- `binary_sensor.annerleyweather_connectivity`
- `binary_sensor.annerleyweather_transmitter_battery`
- `sensor.annerleyweather_dewpoint`
- `sensor.annerleyweather_inside_humidity`
- `sensor.annerleyweather_inside_temperature`
- `sensor.annerleyweather_last_rain_storm`
- `sensor.annerleyweather_last_updated`
- `sensor.annerleyweather_outside_humidity`

Open the **Weather** dashboard on your tablet and confirm cards populate without entity-not-found errors.

## About `custom_components/weatherlink_dashboard`

`custom_components/weatherlink_dashboard/` is currently a **legacy custom integration** and is not required for the repaired dashboard.

Recommendation:

- **Short term:** leave it installed but unused while you confirm the updated dashboard is stable.
- **After validation:** remove the custom integration and any related `sensor: - platform: weatherlink_dashboard` YAML config to avoid confusion and duplicate/invalid entities.


### Custom card dependency for Weather Trends

The weather dashboard now uses `custom:apexcharts-card` for dual-axis Weather Trends charts.

Install via HACS:

1. Go to **HACS → Frontend**.
2. Search for **ApexCharts Card** and install it.
3. Confirm the Lovelace resource is added (usually `/hacsfiles/apexcharts-card/apexcharts-card.js`).
4. Reload the browser cache and refresh dashboards.

## Windy embeds

Windy iframe URLs in `dashboards/weather_dashboard.yaml` are configured with:

- `menu=false`
- `message=false`
- `detail=false`

This reduces UI clutter (especially the bottom forecast/details drawer) and keeps the map tablet-friendly.

## Manual verification checklist

1. Confirm the WeatherLink integration entities above are present in **Developer Tools → States**.
2. Open the weather dashboard and verify no entity cards show “Entity not found”.
3. Confirm Windy maps render and no bottom forecast/details panel slides up.
4. If your WeatherLink integration uses different entity IDs, update the entity IDs in `dashboards/weather_dashboard.yaml` to match your system.

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
