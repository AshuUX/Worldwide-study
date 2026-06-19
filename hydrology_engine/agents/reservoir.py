import numpy as np
import pandas as pd
from .base import HydrologyAgent

class ReservoirAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "reservoir"
        self.max_storage_gwh = 1200.0  # Colbun
        self.current_storage_gwh = 600.0 # Initial 50%
        self._last_run = None
        self._cached_result = None

    def step(self, year, month):
        if (year, month) == self._last_run:
            return self._cached_result
        # Update storage (simplified: assume some inflow-outflow balance)
        # In a real model we'd use flow but let's use seasonal proxy
        seasonal_inflow = 0.1 * np.sin(2 * np.pi * (month - 6) / 12) + 0.05
        self.current_storage_gwh = np.clip(
            self.current_storage_gwh + self.max_storage_gwh * seasonal_inflow,
            0, self.max_storage_gwh
        )

        storage_frac = self.current_storage_gwh / self.max_storage_gwh
        damp = self._dynamic_dampening_factor(storage_frac)

        self._cached_result = {
            "flow_dampening": damp,
            "uncertainty_pct": 0.05,
            "state": {"storage_gwh": self.current_storage_gwh, "dampening": damp}
        }
        self._last_run = (year, month)
        return self._cached_result

    def _dynamic_dampening_factor(self, storage_frac: float,
                                   min_damp: float = 0.75,
                                   max_damp: float = 0.95) -> float:
        return min_damp + (max_damp - min_damp) * storage_frac
