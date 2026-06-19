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

        days = pd.Timestamp(year=year, month=month, day=1).days_in_month
        # Convert mm to m3s
        contribution_m3s = (precip / 1000 * self.basin_area_m2) / (days * 86400)

        return {
            "contribution_m3s": contribution_m3s,
            "uncertainty_pct": 0.15,
            "state": {"precip_mm": precip}
        }
