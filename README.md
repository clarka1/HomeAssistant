# HomeAssistant Dashboards

A collection of [Home Assistant](https://www.home-assistant.io/) Lovelace dashboards, themes, and custom card configurations.

## Repository Structure

```
.
├── dashboards/        # Lovelace dashboard YAML files
│   ├── home.yaml      # Main overview dashboard
│   └── energy.yaml    # Energy monitoring dashboard
├── themes/            # Custom UI themes
│   └── default.yaml   # Default theme
└── custom_cards/      # Custom Lovelace card resources
```

## Setup

### Adding Dashboards

1. Copy the desired YAML files from `dashboards/` to your Home Assistant configuration directory.
2. In Home Assistant, go to **Settings → Dashboards** and add a new dashboard, or edit an existing one by pointing it to the YAML file.
3. Alternatively, use [raw configuration mode](https://www.home-assistant.io/dashboards/dashboards/#using-yaml-for-the-default-dashboard) by adding the following to your `configuration.yaml`:

```yaml
lovelace:
  mode: yaml
  resources: []
  dashboards:
    lovelace-home:
      mode: yaml
      filename: dashboards/home.yaml
      title: Home
      icon: mdi:home
      show_in_sidebar: true
    lovelace-energy:
      mode: yaml
      filename: dashboards/energy.yaml
      title: Energy
      icon: mdi:lightning-bolt
      show_in_sidebar: true
```

### Adding Themes

1. Copy the YAML files from `themes/` to a `themes/` directory in your Home Assistant configuration directory.
2. Add the following to your `configuration.yaml`:

```yaml
frontend:
  themes: !include_dir_merge_named themes/
```

3. Restart Home Assistant and select your theme via **Profile → Theme**.

### Custom Cards

See [`custom_cards/README.md`](custom_cards/README.md) for instructions on adding custom Lovelace cards.

## Contributing

1. Fork this repository.
2. Create a branch for your changes.
3. Add or modify dashboard YAML files.
4. Submit a pull request with a description of your changes.

