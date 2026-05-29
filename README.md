# HomeAssistant Dashboards

Configuration and Lovelace dashboard files for the Annerley smart home.

Home Assistant is the complete smart-home inventory. Apple Home/HomeKit remains
the broad Siri-facing control surface, but native HomeKit accessories should not
be removed or re-paired unless there is no alternative. This is especially
important for LIFX downlights, because physical pairing codes may be difficult
to access.

## Repository Structure

```text
.
├── dashboards/
│   ├── home.yaml                 # Daily cockpit plus room views
│   ├── energy.yaml               # Built-in Home Assistant energy cards
│   └── weather_dashboard.yaml    # Davis/WeatherLink dashboard
├── packages/
│   └── weather_rain.yaml         # Yesterday-rain helper sensors
├── themes/
│   └── default.yaml
├── custom_cards/
└── custom_components/
    └── weatherlink_dashboard/    # Legacy custom integration, not required
```

## Current Live Context

Last live inventory used for this repo update:

- Home Assistant: `2026.3.1`
- Time zone: `Australia/Brisbane`
- Weather station: Davis Vantage Vue / WeatherLink, device `Annerley`
- Important integrations: `weatherlink`, `lifx`, `sensibo`, `dyson_local`,
  `aarlo`, `lg_thinq`, `webostv`, `homekit`, `apple_tv`, `cast`
- Registry scale at audit time: 10 areas, 81 devices, 468 entity-registry rows

The room model should follow the unit floor plan:

- `Bedroom` means the main bedroom / Bed 1.
- `Lexi's Room` means Bedroom 2.
- `Bathroom` means the ensuite.
- The main bathroom/Lexi's bathroom currently has no smart lights and does not
  need a separate active dashboard room.
- `Lounge`, `Kitchen`, `Courtyard`, `Hallway`, `Laundry`, and `Wardrobe` are
  physical spaces.
- `Living Areas`, `Living Room`, `Lounge Room`, and `lexis` are migration
  buckets/naming leftovers, not long-term canonical room names.

## Weather Dashboard

`dashboards/weather_dashboard.yaml` is wired to the live WeatherLink entities:

- `binary_sensor.annerleyweather_connectivity`
- `binary_sensor.annerleyweather_transmitter_battery`
- `sensor.annerleyweather_dewpoint`
- `sensor.annerleyweather_inside_humidity`
- `sensor.annerleyweather_inside_temperature`
- `sensor.annerleyweather_last_rain_storm`
- `sensor.annerleyweather_last_updated`
- `sensor.annerleyweather_outside_humidity`
- `sensor.annerleyweather_outside_temperature`
- `sensor.annerleyweather_pressure`
- `sensor.annerleyweather_rain_intensity`
- `sensor.annerleyweather_rain_storm`
- `sensor.annerleyweather_rain_this_month`
- `sensor.annerleyweather_rain_this_year`
- `sensor.annerleyweather_rain_today`
- `sensor.annerleyweather_solar_panel`
- `sensor.annerleyweather_supercapacitor`
- `sensor.annerleyweather_transmitter_battery`
- `sensor.annerleyweather_wind`
- `sensor.annerleyweather_wind_direction`
- `sensor.annerleyweather_wind_gust`

The dashboard also expects the helper sensor from `packages/weather_rain.yaml`:

- `sensor.annerley_rain_yesterday`

### Yesterday's Rain

`packages/weather_rain.yaml` creates:

- `sensor.annerley_rain_daily`, a daily utility meter sourced from
  `sensor.annerleyweather_rain_this_year`
- `sensor.annerley_rain_yesterday`, a template sensor showing the previous
  completed daily cycle from the utility meter's `last_period` attribute

The first daily cycle after deployment may be incomplete. The value becomes
fully reliable after the first midnight reset.

## Home Dashboard

`dashboards/home.yaml` now starts with a daily cockpit and then room views.

The cockpit surfaces:

- Weather and rain, including yesterday's rainfall
- Arlo cameras, battery, and connectivity
- Sensibo climate controls
- Dyson temperature, humidity, air quality, and filter status
- LIFX lights
- LG washer state
- Media devices
- A watch list for stale/unavailable devices

Room views are:

- Lounge
- Kitchen
- Bedroom
- Lexi's Room
- Courtyard
- Hallway
- Laundry
- Wardrobe

## HomeKit / Apple Home Guidance

The preferred model is broad mirroring: most HomeKit-supported Home Assistant
controls should be visible in Apple Home/Siri.

Constraints:

- Do not remove native HomeKit accessories if re-adding them could require a
  physical pairing code.
- Prefer renaming and room moves in Home Assistant and Apple Home before
  considering bridge rebuilds.
- HomeKit may cache accessory names after first pairing. Some name cleanup may
  not fully appear until the relevant Home Assistant-created bridge/accessory is
  re-paired.
- Home Assistant-created bridges seen during audit were `HASS Bridge:21064`,
  `TV:21065`, `Chromecast:21066`, and `Chromecast:21067`.
- TV-like media players, remotes, locks, and cameras may need HomeKit accessory
  mode rather than normal bridge mode.
- If a bridge/accessory rebuild is needed, rebuild only Home Assistant-created
  HomeKit entries where re-pairing does not require LIFX/native HomeKit codes.

Recommended cleanup order:

1. Fix Home Assistant area assignments and friendly names first.
2. Reload dashboards and verify the daily cockpit.
3. In Apple Home, move accessories into the canonical rooms and merge
   `Lounge Room` into `Lounge`.
4. Keep `Lexi's Room` as the Apple Home room for Bedroom 2; do not use `lexis`.
5. Only after names/rooms are stable, review Home Assistant-created HomeKit
   bridge/accessory duplicates.

## Deployment

Copy or sync these files into Home Assistant:

- `dashboards/home.yaml` -> `/config/dashboards/home.yaml`
- `dashboards/weather_dashboard.yaml` -> `/config/dashboards/weather_dashboard.yaml`
- `dashboards/energy.yaml` -> `/config/dashboards/energy.yaml`
- `packages/weather_rain.yaml` -> `/config/packages/weather_rain.yaml`

Enable packages if they are not already enabled:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

Register dashboards if they are not already registered:

```yaml
lovelace:
  mode: yaml
  dashboards:
    lovelace-home:
      mode: yaml
      filename: dashboards/home.yaml
      title: Home
      icon: mdi:home-assistant
      show_in_sidebar: true
    lovelace-weather:
      mode: yaml
      filename: dashboards/weather_dashboard.yaml
      title: Weather
      icon: mdi:weather-partly-rainy
      show_in_sidebar: true
    lovelace-energy:
      mode: yaml
      filename: dashboards/energy.yaml
      title: Energy
      icon: mdi:lightning-bolt
      show_in_sidebar: true
```

After copying:

1. Run Home Assistant `homeassistant.check_config`.
2. Reload core config or restart if packages were newly enabled.
3. Reload YAML dashboards or restart Home Assistant.
4. Confirm the weather and home dashboards show no `Entity not found` cards.
5. Confirm `sensor.annerley_rain_yesterday` appears after the utility meter has
   completed a daily cycle.

## Validation

Run the repo contract tests locally:

```bash
ruby test/test_config_contract.rb
```

The tests parse the YAML and assert that the rain package and core dashboard
entities are present.

During the implementation audit, all dashboard entity references were compared
against the live Home Assistant state snapshot, with `sensor.annerley_rain_daily`
and `sensor.annerley_rain_yesterday` treated as newly defined.

## Legacy Custom WeatherLink Component

`custom_components/weatherlink_dashboard/` is currently legacy and not required
for the repaired dashboards. Keep it installed but unused until the WeatherLink
integration and new dashboards are stable; then remove the custom integration
and any related `sensor: - platform: weatherlink_dashboard` YAML config if it is
still present in live Home Assistant.

## Themes and Custom Cards

To use themes:

```yaml
frontend:
  themes: !include_dir_merge_named themes/
```

Custom cards, if needed later, should be documented in `custom_cards/README.md`.
