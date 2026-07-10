"""Sensor platform voor SocSense met spreidings-ondersteuning."""
from __future__ import annotations
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SocSenseCoordinator, SocSenseData

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: SocSenseCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        SocForecastSensor(coordinator, entry),
        SocForecastMinSensor(coordinator, entry),
        SocForecastMaxSensor(coordinator, entry),
        HomeUsageForecastSensor(coordinator, entry),
        HomeUsageForecastMinSensor(coordinator, entry),
        HomeUsageForecastMaxSensor(coordinator, entry),
    ]
    async_add_entities(entities)

class _BaseForecastSensor(CoordinatorEntity[SocSenseCoordinator], SensorEntity):
    _attr_has_entity_name = True
    
    def __init__(self, coordinator: SocSenseCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="SocSense",
            manufacturer="BryanGeldof",
            model="SOC Forecast Engine",
        )

# --- SOC Sensoren ---
class SocForecastSensor(_BaseForecastSensor):
    _attr_name = "SOC Forecast"
    _attr_state_class = SensorStateClass.MEASUREMENT
    @property
    def native_value(self): return round(self.coordinator.data.soc[0], 1)

class SocForecastMinSensor(_BaseForecastSensor):
    _attr_name = "SOC Forecast Min"
    @property
    def native_value(self): return round(min(self.coordinator.data.soc_min), 1)

class SocForecastMaxSensor(_BaseForecastSensor):
    _attr_name = "SOC Forecast Max"
    @property
    def native_value(self): return round(max(self.coordinator.data.soc_max), 1)

# --- Usage Sensoren ---
class HomeUsageForecastSensor(_BaseForecastSensor):
    _attr_name = "Usage Forecast"
    _attr_state_class = SensorStateClass.MEASUREMENT
    @property
    def native_value(self): return round(self.coordinator.data.home_usage_w[0], 1)

class HomeUsageForecastMinSensor(_BaseForecastSensor):
    _attr_name = "Usage Forecast Min"
    @property
    def native_value(self): 
        # Bereken min van het usage scenario
        return round(min(self.coordinator.data.home_usage_min), 1)

class HomeUsageForecastMaxSensor(_BaseForecastSensor):
    _attr_name = "Usage Forecast Max"
    @property
    def native_value(self): 
        # Bereken max van het usage scenario
        return round(max(self.coordinator.data.home_usage_max), 1)
