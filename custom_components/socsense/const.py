"""Constants for the SocSense integration."""
from datetime import timedelta

DOMAIN = "socsense"
PLATFORMS = ["sensor"]

# --- Config keys (deze worden opgeslagen in de config entry van de gebruiker) ---
CONF_HOME_USAGE_SENSOR = "home_usage_sensor"
CONF_SOLAR_FORECAST_SENSOR = "solar_forecast_sensor"

CONF_BATTERY_SOC_SENSOR = "battery_soc_sensor"
CONF_BATTERY_CAPACITY = "battery_capacity_kwh"
CONF_BATTERY_MIN_SOC = "battery_min_soc"
CONF_BATTERY_MAX_SOC = "battery_max_soc"
CONF_BATTERY_EFFICIENCY = "battery_efficiency"
CONF_BATTERY_MAX_CHARGE_POWER = "battery_max_charge_power"
CONF_BATTERY_MAX_DISCHARGE_POWER = "battery_max_discharge_power"
CONF_BATTERY_CHARGE_POWER_SENSOR = "battery_charge_power_sensor"
CONF_BATTERY_DISCHARGE_POWER_SENSOR = "battery_discharge_power_sensor"

CONF_HISTORY_DAYS = "history_days"
CONF_SIMILAR_DAY_COUNT = "similar_day_count"

# --- Standaardwaarden (Fallback als de gebruiker niets invult) ---
# Deze waarden worden in de UI getoond als placeholder
DEFAULT_BATTERY_CAPACITY = 5.0
DEFAULT_BATTERY_MIN_SOC = 10.0
DEFAULT_BATTERY_MAX_SOC = 100.0
DEFAULT_BATTERY_EFFICIENCY = 90.0
DEFAULT_MAX_CHARGE_POWER = 2500.0
DEFAULT_MAX_DISCHARGE_POWER = 2500.0
DEFAULT_HISTORY_DAYS = 42
DEFAULT_SIMILAR_DAY_COUNT = 4

# --- Systeem instellingen ---
INTERVAL_MINUTES = 15
FORECAST_HORIZON_HOURS = 24 * 7
UPDATE_INTERVAL = timedelta(minutes=10)

# --- Validatie grenzen voor de Config Flow ---
# Hiermee voorkom je dat gebruikers onmogelijke waarden invullen
MIN_BATTERY_CAPACITY = 0.1
MAX_BATTERY_CAPACITY = 1000.0
