require "minitest/autorun"
require "yaml"

ROOT = File.expand_path("..", __dir__)

def load_yaml(path)
  YAML.safe_load(File.read(File.join(ROOT, path)), aliases: true)
end

def deep_entity_ids(value)
  case value
  when Hash
    value.flat_map do |key, child|
      [key == "entity" ? child : nil, *deep_entity_ids(child)]
    end.compact
  when Array
    value.flat_map { |child| deep_entity_ids(child) }
  else
    []
  end
end

class ConfigContractTest < Minitest::Test
  def test_weather_rain_package_defines_yesterday_sensor
    package = load_yaml("packages/weather_rain.yaml")

    assert_equal "sensor.annerleyweather_rain_this_year",
                 package.fetch("utility_meter").fetch("annerley_rain_daily").fetch("source")

    sensors = package.fetch("template").flat_map { |entry| entry.fetch("sensor", []) }
    yesterday = sensors.find { |sensor| sensor["unique_id"] == "annerley_rain_yesterday" }

    refute_nil yesterday
    assert_equal "Annerley Rain Yesterday", yesterday.fetch("name")
    assert_includes yesterday.fetch("state"), "last_period"
  end

  def test_weather_dashboard_surfaces_core_davis_console_values
    dashboard = load_yaml("dashboards/weather_dashboard.yaml")
    entity_ids = deep_entity_ids(dashboard)

    %w[
      sensor.annerleyweather_outside_temperature
      sensor.annerleyweather_inside_temperature
      sensor.annerleyweather_rain_today
      sensor.annerley_rain_yesterday
      sensor.annerleyweather_rain_storm
      sensor.annerleyweather_rain_this_month
      sensor.annerleyweather_rain_this_year
      sensor.annerleyweather_wind
      sensor.annerleyweather_pressure
    ].each do |entity_id|
      assert_includes entity_ids, entity_id
    end
  end

  def test_home_dashboard_uses_live_entities_and_room_views
    dashboard = load_yaml("dashboards/home.yaml")
    views = dashboard.fetch("views")
    paths = views.map { |view| view.fetch("path") }

    %w[
      cockpit
      lounge
      kitchen
      bedroom
      lexis-room
      courtyard
      laundry
    ].each do |path|
      assert_includes paths, path
    end

    entity_ids = deep_entity_ids(dashboard)
    %w[
      weather.forecast_home
      sensor.annerley_rain_yesterday
      camera.aarlo_courtyard
      camera.aarlo_patio
      climate.lounge
      climate.bedroom
      fan.dyson_pure_hot_cooltm
      sensor.front_load_washer_current_status
      media_player.lg_speaker_sp11ra
      light.lounge_lamp
    ].each do |entity_id|
      assert_includes entity_ids, entity_id
    end
  end
end
