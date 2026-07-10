"""Forecasting engine voor SocSense met spreiding (Min/Max)."""
from __future__ import annotations
import math
from datetime import datetime
from .const import INTERVAL_MINUTES

def simulate_soc_with_spread(
    timestamps: list[datetime],
    home_usage_w: list[float],
    solar_w_list: list[list[float]],  # Nu een lijst van lijsten (meerdere scenario's)
    usage_w_list: list[list[float]],  # Nu een lijst van lijsten (meerdere scenario's)
    start_soc: float,
    capacity_kwh: float,
    min_soc: float,
    max_soc: float,
    efficiency_pct: float,
    max_charge_w: float,
    max_discharge_w: float,
) -> tuple[list[float], list[float], list[float]]:
    """Simuleert batterij SOC voor gemiddelde, min en max scenario's."""
    
    efficiency = max(0.5, min(1.0, efficiency_pct / 100))
    hours_per_step = INTERVAL_MINUTES / 60
    
    all_series = []
    
    # Bereken voor elk scenario (Gemiddelde, Min, Max)
    for usage_scenario, solar_scenario in zip(usage_w_list, solar_w_list):
        soc = start_soc
        series = []
        for usage_w, sun_w in zip(usage_scenario, solar_scenario):
            net_w = sun_w - usage_w
            
            # Batterij logica
            if net_w > 0: # Laden
                headroom_kwh = (max_soc - soc) / 100 * capacity_kwh
                charge_kwh = min(net_w * hours_per_step / 1000, headroom_kwh / efficiency if efficiency else 0)
                soc += (charge_kwh * efficiency / capacity_kwh) * 100
            else: # Ontladen
                available_kwh = (soc - min_soc) / 100 * capacity_kwh
                discharge_kwh = min(abs(net_w) * hours_per_step / 1000, available_kwh)
                soc -= (discharge_kwh / capacity_kwh) * 100
            
            soc = max(min_soc, min(max_soc, soc))
            series.append(soc)
        all_series.append(series)

    # all_series[0] is avg, [1] is min, [2] is max
    return all_series[0], all_series[1], all_series[2]
