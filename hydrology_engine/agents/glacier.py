import numpy as np
import pandas as pd
from .base import HydrologyAgent

class GlacierAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "glacier"
        self.area_km2 = 580
        self.monthly_melt_dist = {
            1: 0.22, 2: 0.20, 3: 0.12, 4: 0.05, 5: 0.01, 6: 0.00,
            7: 0.00, 8: 0.01, 9: 0.04, 10: 0.10, 11: 0.13, 12: 0.12
        }

    def step(self, year, month):
        base_melt_m_we_yr = 0.85
        trend = (year - 1980) / 10 * 0.02 if year > 1980 else 0

        annual_melt_m3 = (base_melt_m_we_yr + trend) * self.area_km2 * 1e6
        monthly_melt_m3 = annual_melt_m3 * self.monthly_melt_dist[month]

        days = pd.Timestamp(year=year, month=month, day=1).days_in_month
        contribution_m3s = monthly_melt_m3 / (days * 86400)

        return {
            "contribution_m3s": contribution_m3s,
            "uncertainty_pct": 0.25,
            "state": {"annual_melt_m3": annual_melt_m3}
        }
