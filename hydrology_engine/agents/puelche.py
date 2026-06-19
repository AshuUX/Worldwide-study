import numpy as np
import pandas as pd
from .base import HydrologyAgent

class PuelcheAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "puelche"
        self.active_months = {8, 9, 10, 11}

    def step(self, year, month):
        if month not in self.active_months:
            return {"melt_accelerator": 1.0, "precip_suppressor": 1.0, "uncertainty_pct": 0.05, "state": {}}

        temp = self._get_var("temp_c", year, month)
        temp_clim = self._climatological_mean("temp_c", month)
        temp_anomaly = temp - temp_clim if not pd.isna(temp) and not pd.isna(temp_clim) else 0.0

        puelche_intensity = np.clip(temp_anomaly / 3.0, 0.0, 1.0)

        melt_accelerator = 1.0 + (0.35 * puelche_intensity)
        precip_suppressor = 1.0 - (0.20 * puelche_intensity)

        return {
            "melt_accelerator": melt_accelerator,
            "precip_suppressor": precip_suppressor,
            "uncertainty_pct": 0.20,
            "state": {"puelche_intensity": puelche_intensity}
        }
