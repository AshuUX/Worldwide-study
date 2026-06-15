import numpy as np
import pandas as pd
from .base import HydrologyAgent

class AAOAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "aao"
        self.seasonal_weights = {
            1: 0.2, 2: 0.2, 3: 0.3, 4: 0.6, 5: 0.8, 6: 1.0,
            7: 1.0, 8: 0.9, 9: 0.7, 10: 0.5, 11: 0.3, 12: 0.2
        }

    def step(self, year, month):
        aao = self._get_index("aao_index", year, month)
        if pd.isna(aao):
            return {"contribution_multiplier": 1.0, "uncertainty_pct": 0.12, "state": {"aao_value": 0}}

        w = self.seasonal_weights[month]
        precip_anomaly = -0.15 * np.tanh(aao) * w
        flow_multiplier = 1.0 + precip_anomaly * 1.2

        return {
            "contribution_multiplier": np.clip(flow_multiplier, 0.5, 1.5),
            "uncertainty_pct": 0.12,
            "state": {"aao_value": aao}
        }
