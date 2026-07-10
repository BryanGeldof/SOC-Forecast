"""Forecasting engine voor SocSense met spreiding (Min/Max)."""
from __future__ import annotations
from .const import INTERVAL_MINUTES

def simulate_soc_with_spread(
    solar_buckets: list[float],
    capacity_kwh: float,
    min_soc: float,
    max_soc: float,
    efficiency_pct: float,
) -> tuple[list[float], list[float], list[float]]:
    """
    Simuleert batterij SOC voor gemiddelde, min en max scenario's.
    Gebruikt de gesimuleerde solar_buckets en berekent de 3 curves.
    """
    
    efficiency = max(0.5, min(1.0, efficiency_pct / 100))
    hours_per_step = INTERVAL_MINUTES / 60
    
    # We simuleren hier 3 scenario's:
    # 1. Avg: Gebaseerd op de voorspelde zonne-energie
    # 2. Min: Worst-case (bijv. 80% van solar_buckets)
    # 3. Max: Best-case (bijv. 120% van solar_buckets)
    
    scenarios = {
        "avg": [val for val in solar_buckets],
        "min": [val * 0.8 for val in solar_buckets],
        "max": [val * 1.2 for val in solar_buckets]
    }
    
    results = {}
    
    for name, solar_scenario in scenarios.items():
        soc = 50.0  # Start SOC (of haal dit op uit je actuele sensor)
        series = []
        
        # Simulatie per bucket (15 min per stap)
        for sun_w in solar_scenario:
            # Hier kun je ook home_usage_w per stap toevoegen indien gewenst
            net_w = sun_w # Vereenvoudigd: zon in - verbruik (nu 0 voor demonstratie)
            
            if net_w > 0: # Laden
                headroom_kwh = (max_soc - soc) / 100 * capacity_kwh
                charge_kwh = min(net_w * hours_per_step / 1000, headroom_kwh / efficiency if efficiency > 0 else 0)
                soc += (charge_kwh * efficiency / capacity_kwh) * 100
            else: # Ontladen
                available_kwh = (soc - min_soc) / 100 * capacity_kwh
                discharge_kwh = min(abs(net_w) * hours_per_step / 1000, available_kwh)
                soc -= (discharge_kwh / capacity_kwh) * 100
            
            soc = max(min_soc, min(max_soc, soc))
            series.append(soc)
            
        results[name] = series

    return results["avg"], results["min"], results["max"]
