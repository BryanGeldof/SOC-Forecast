"""DataUpdateCoordinator voor SocSense."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from . import forecast as fc
from .const import (
    CONF_BATTERY_CAPACITY, CONF_BATTERY_CHARGE_POWER_SENSOR,
    CONF_BATTERY_DISCHARGE_POWER_SENSOR, CONF_BATTERY_EFFICIENCY,
    CONF_BATTERY_MAX_CHARGE_POWER, CONF_BATTERY_MAX_DISCHARGE_POWER,
    CONF_BATTERY_MIN_SOC, CONF_BATTERY_MAX_SOC, CONF_SOLAR_FORECAST_SENSOR,
    DOMAIN, DEFAULT_BATTERY_EFFICIENCY, DEFAULT_MAX_CHARGE_POWER,
    DEFAULT_MAX_DISCHARGE_POWER, UPDATE_INTERVAL
)

_LOGGER = logging.getLogger(__name__)

@dataclass
class SocSenseData:
    timestamps: list
    soc: list[float]
    soc_min: list[float]
    soc_max: list[float]
    home_usage_w: list[float]
    home_usage_min: list[float]
    home_usage_max: list[float]
    solar_w: list[float]
    matched_day: str | None
    scale_factor: float

class SocSenseCoordinator(DataUpdateCoordinator[SocSenseData]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=UPDATE_INTERVAL)
        self.entry = entry

    async def _async_update_data(self) -> SocSenseData:
        cfg = self.entry.data
        
        # 1. Config ophalen
        capacity_kwh = cfg.get(CONF_BATTERY_CAPACITY, 5.0)
        min_soc = cfg.get(CONF_BATTERY_MIN_SOC, 10.0)
        max_soc = cfg.get(CONF_BATTERY_MAX_SOC, 100.0)
        efficiency = cfg.get(CONF_BATTERY_EFFICIENCY, DEFAULT_BATTERY_EFFICIENCY)
        
        # 2. Solcast curve ophalen en resamplen naar 96 buckets
        solcast_entity = cfg.get(CONF_SOLAR_FORECAST_SENSOR)
        solar_buckets = self._get_solcast_buckets(solcast_entity)
        
        # 3. Simulatie uitvoeren met de 3 lijsten (Unpacking lost 'not defined' error op)
        # Zorg dat je forecast.py deze 3 lijsten teruggeeft
        soc_avg, soc_min, soc_max = fc.simulate_soc_with_spread(
            solar_buckets, capacity_kwh, min_soc, max_soc, efficiency
        )
        
        return SocSenseData(
            timestamps=[], # Vul hier je timestamps in
            soc=soc_avg,
            soc_min=soc_min,
            soc_max=soc_max,
            home_usage_w=[], # Vul hier je verbruik in
            solar_w=solar_buckets,
            matched_day=None,
            scale_factor=1.0
        )

    def _get_solcast_buckets(self, entity_id: str) -> list[float]:
        """Extraheert Solcast forecast en resampled naar 96 buckets van 15min."""
        state = self.hass.states.get(entity_id)
        if not state or "forecast" not in state.attributes:
            return [0.0] * 96
        
        raw_forecast = state.attributes.get("forecast", [])
        buckets = []
        for entry in raw_forecast:
            # Verdeel uurtarief over 4 kwartieren (15 min per bucket)
            val_per_15min = float(entry.get("pv_estimate", 0)) / 4
            buckets.extend([val_per_15min] * 4)
            
        return buckets[:96] # Garandeer 24u data

    def _resolve_power(self, sensor_entity: str | None, fallback: float) -> float:
        if sensor_entity and (state := self.hass.states.get(sensor_entity)):
            try:
                return abs(float(state.state))
            except (TypeError, ValueError):
                pass
        return float(fallback)
