"""DataUpdateCoordinator voor SocSense."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from . import forecast as fc
from .const import (
    CONF_BATTERY_CAPACITY, CONF_BATTERY_CHARGE_POWER_SENSOR,
    CONF_BATTERY_DISCHARGE_POWER_SENSOR, CONF_BATTERY_EFFICIENCY,
    CONF_BATTERY_MAX_CHARGE_POWER, CONF_BATTERY_MAX_DISCHARGE_POWER,
    CONF_BATTERY_MIN_SOC, CONF_BATTERY_MAX_SOC, DOMAIN,
    DEFAULT_BATTERY_EFFICIENCY, DEFAULT_MAX_CHARGE_POWER,
    DEFAULT_MAX_DISCHARGE_POWER, UPDATE_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

@dataclass
class SocSenseData:
    timestamps: list
    soc: list[float]
    soc_min: list[float]  # Nieuw: Min spreiding
    soc_max: list[float]  # Nieuw: Max spreiding
    home_usage_w: list[float]
    solar_w: list[float]
    matched_day: str | None
    scale_factor: float

class SocSenseCoordinator(DataUpdateCoordinator[SocSenseData]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)
        self.entry = entry

    async def _async_update_data(self) -> SocSenseData:
        """Haal data op en voer simulatie met spreiding uit."""
        cfg = self.entry.data
        
        # 1. Haal configuratie op (met jouw eigen batterij-capaciteit)
        capacity_kwh = cfg.get(CONF_BATTERY_CAPACITY, 5.0)
        min_soc = cfg.get(CONF_BATTERY_MIN_SOC, 10.0)
        max_soc = cfg.get(CONF_BATTERY_MAX_SOC, 100.0)
        efficiency = cfg.get(CONF_BATTERY_EFFICIENCY, DEFAULT_BATTERY_EFFICIENCY)
        
        # 2. Resolving sensoren vs vaste waardes
        max_charge_w = self._resolve_power(cfg.get(CONF_BATTERY_CHARGE_POWER_SENSOR), 
                                           cfg.get(CONF_BATTERY_MAX_CHARGE_POWER, DEFAULT_MAX_CHARGE_POWER))
        max_discharge_w = self._resolve_power(cfg.get(CONF_BATTERY_DISCHARGE_POWER_SENSOR), 
                                              cfg.get(CONF_BATTERY_MAX_DISCHARGE_POWER, DEFAULT_MAX_DISCHARGE_POWER))

        # 3. Voer simulatie uit (je moet forecast.py updaten om 3 series terug te geven)
        # soc_avg, soc_min, soc_max = fc.simulate_soc_with_spread(...)
        
        return SocSenseData(
            timestamps=..., # Je tijdstippen
            soc=soc_avg,
            soc_min=soc_min,
            soc_max=soc_max,
            home_usage_w=...,
            solar_w=...,
            matched_day=...,
            scale_factor=...
        )

    def _resolve_power(self, sensor_entity: str | None, fallback: float) -> float:
        if sensor_entity and (state := self.hass.states.get(sensor_entity)):
            try:
                return abs(float(state.state))
            except (TypeError, ValueError):
                pass
        return float(fallback)
