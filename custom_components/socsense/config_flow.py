"""Config flow for SocSense."""
from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_BATTERY_CAPACITY,
    CONF_BATTERY_CHARGE_POWER_SENSOR,
    CONF_BATTERY_DISCHARGE_POWER_SENSOR,
    CONF_BATTERY_EFFICIENCY,
    CONF_BATTERY_MAX_CHARGE_POWER,
    CONF_BATTERY_MAX_DISCHARGE_POWER,
    CONF_BATTERY_MIN_SOC,
    CONF_BATTERY_MAX_SOC,
    CONF_BATTERY_SOC_SENSOR,
    CONF_HISTORY_DAYS,
    CONF_HOME_USAGE_SENSOR,
    CONF_SIMILAR_DAY_COUNT,
    CONF_SOLAR_FORECAST_SENSOR,
    DEFAULT_BATTERY_EFFICIENCY,
    DEFAULT_BATTERY_MAX_SOC,
    DEFAULT_BATTERY_MIN_SOC,
    DEFAULT_HISTORY_DAYS,
    DEFAULT_MAX_CHARGE_POWER,
    DEFAULT_MAX_DISCHARGE_POWER,
    DEFAULT_SIMILAR_DAY_COUNT,
    DOMAIN,
)

def _core_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_HOME_USAGE_SENSOR, default=defaults.get(CONF_HOME_USAGE_SENSOR)): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        vol.Required(CONF_SOLAR_FORECAST_SENSOR, default=defaults.get(CONF_SOLAR_FORECAST_SENSOR)): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        vol.Required(CONF_HISTORY_DAYS, default=defaults.get(CONF_HISTORY_DAYS, DEFAULT_HISTORY_DAYS)): vol.All(vol.Coerce(int), vol.Range(min=7, max=365)),
        vol.Required(CONF_SIMILAR_DAY_COUNT, default=defaults.get(CONF_SIMILAR_DAY_COUNT, DEFAULT_SIMILAR_DAY_COUNT)): vol.All(vol.Coerce(int), vol.Range(min=1, max=10)),
    })

def _battery_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_BATTERY_SOC_SENSOR, default=defaults.get(CONF_BATTERY_SOC_SENSOR)): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        vol.Required(CONF_BATTERY_CAPACITY, default=defaults.get(CONF_BATTERY_CAPACITY, 5.0)): vol.All(vol.Coerce(float), vol.Range(min=0.1, max=1000.0)),
        vol.Required(CONF_BATTERY_MIN_SOC, default=defaults.get(CONF_BATTERY_MIN_SOC, DEFAULT_BATTERY_MIN_SOC)): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
        vol.Required(CONF_BATTERY_MAX_SOC, default=defaults.get(CONF_BATTERY_MAX_SOC, DEFAULT_BATTERY_MAX_SOC)): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
        vol.Required(CONF_BATTERY_EFFICIENCY, default=defaults.get(CONF_BATTERY_EFFICIENCY, DEFAULT_BATTERY_EFFICIENCY)): vol.All(vol.Coerce(float), vol.Range(min=50, max=100)),
        vol.Required(CONF_BATTERY_MAX_CHARGE_POWER, default=defaults.get(CONF_BATTERY_MAX_CHARGE_POWER, DEFAULT_MAX_CHARGE_POWER)): vol.Coerce(float),
        vol.Required(CONF_BATTERY_MAX_DISCHARGE_POWER, default=defaults.get(CONF_BATTERY_MAX_DISCHARGE_POWER, DEFAULT_MAX_DISCHARGE_POWER)): vol.Coerce(float),
        vol.Optional(CONF_BATTERY_CHARGE_POWER_SENSOR, default=defaults.get(CONF_BATTERY_CHARGE_POWER_SENSOR, "")): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
        vol.Optional(CONF_BATTERY_DISCHARGE_POWER_SENSOR, default=defaults.get(CONF_BATTERY_DISCHARGE_POWER_SENSOR, "")): selector.EntitySelector(selector.EntitySelectorConfig(domain="sensor")),
    })

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    
    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> config_entries.FlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_battery()
        return self.async_show_form(step_id="user", data_schema=_core_schema({}))

    async def async_step_battery(self, user_input: dict[str, Any] | None = None) -> config_entries.FlowResult:
        errors = {}
        if user_input is not None:
            if user_input[CONF_BATTERY_MIN_SOC] >= user_input[CONF_BATTERY_MAX_SOC]:
                errors["base"] = "min_soc_above_max_soc"
            else:
                self._data.update(user_input)
                return self.async_create_entry(title="SocSense Battery", data=self._data)
        
        return self.async_show_form(step_id="battery", data_schema=_battery_schema({}), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry
        self._data = dict(config_entry.data)

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> config_entries.FlowResult:
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title="", data=self._data)
        return self.async_show_form(step_id="init", data_schema=_battery_schema(self._data))
