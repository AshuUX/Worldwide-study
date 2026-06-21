import numpy as np
import pandas as pd
from .base import HydrologyAgent

class PrecipAnomalyAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "precip_anomaly"
        self.basin_area_m2 = 20_300 * 1e6

    def step(self, year, month):
        precip = self._get_var("precip_mm", year, month)
        if pd.isna(precip):
            precip = 0

        # BUG FIX: Precip contrib should be MUCH smaller than basin-wide area multiplication
        # because most precip doesn't run off immediately.
        # Let's apply a baseline 0.1 scaling if not handled by interaction.
        days = pd.Timestamp(year=year, month=month, day=1).days_in_month
        contribution_m3s = (precip / 1000 * self.basin_area_m2 * 0.01) / (days * 86400)

        return {
            "contribution_m3s": contribution_m3s,
            "uncertainty_pct": 0.15,
            "state": {"precip_mm": precip}
        }
