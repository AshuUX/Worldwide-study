import numpy as np
import pandas as pd
from .base import HydrologyAgent

class ENSOAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "enso"
        # Regression coefficients from Montecinos & Aceituno (2003)
        self.mei_to_precip_coeff = -0.18  # each unit MEI → -18% precip anomaly
        self.precip_to_flow_elasticity = 1.4  # 1% precip change → 1.4% flow change
        # seasonal modulation — ENSO effect stronger in austral winter/spring
        self.seasonal_weights = {
            1: 0.6, 2: 0.5, 3: 0.7, 4: 0.9, 5: 1.1, 6: 1.2,
            7: 1.2, 8: 1.1, 9: 1.0, 10: 0.8, 11: 0.7, 12: 0.6
        }

    def step(self, year: int, month: int) -> dict:
        # get 6-month lagged MEI
        lag_date = pd.Timestamp(year=year, month=month, day=1) - pd.DateOffset(months=6)
        mei = self._get_index("enso_mei", lag_date.year, lag_date.month)

        if pd.isna(mei):
            return {"contribution_multiplier": 1.0, "uncertainty_pct": 0.15, "state": {"enso_phase": "unknown"}}

        # compute flow multiplier
        seasonal_w = self.seasonal_weights[month]
        precip_anomaly_pct = self.mei_to_precip_coeff * mei * seasonal_w
        flow_multiplier = 1.0 + (precip_anomaly_pct * self.precip_to_flow_elasticity)
        flow_multiplier = np.clip(flow_multiplier, 0.3, 2.0)  # physical bounds

        # classify phase for interaction layer
        if mei > 0.5:
            phase = "el_nino"
        elif mei < -0.5:
            phase = "la_nina"
        else:
            phase = "neutral"

        return {
            "contribution_multiplier": flow_multiplier,
            "uncertainty_pct": 0.10 + abs(mei) * 0.03,
            "state": {"enso_phase": phase, "mei_value": mei}
        }
