import numpy as np
import pandas as pd
from .base import HydrologyAgent

class PDOAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "pdo"

    def step(self, year, month):
        pdo_smooth = self._rolling_mean("pdo_index", year, month, window=12)

        if pd.isna(pdo_smooth):
            return {"contribution_multiplier": 1.0, "uncertainty_pct": 0.08, "state": {"pdo_phase": "neutral", "pdo_value": 0}}

        base_multiplier = 1.0 + (-0.08 * np.sign(pdo_smooth) * min(abs(pdo_smooth), 2.0))

        return {
            "contribution_multiplier": base_multiplier,
            "uncertainty_pct": 0.08,
            "state": {"pdo_phase": "positive" if pdo_smooth > 0 else "negative", "pdo_value": pdo_smooth}
        }
