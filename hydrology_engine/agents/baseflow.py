import numpy as np
import pandas as pd
from .base import HydrologyAgent

class BaseflowAgent(HydrologyAgent):
    """
    Linear reservoir recession model for groundwater baseflow.
    Recharged by soil moisture drainage, depletes slowly via recession constant.
    """
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "baseflow"
        # recession constant — fraction of baseflow storage retained each month
        self.recession_constant = 0.92
        # fraction of soil moisture drainage that recharges baseflow storage
        self.recharge_fraction = 0.15
        # initialise storage at a reasonable starting value (mm equivalent)
        self.storage_mm = 120.0
        self.basin_area_km2 = 20_300  # Maule
        self._last_run = None
        self._cached_result = None

    def step(self, year: int, month: int, soil_drainage_mm: float = None) -> dict:
        if (year, month) == self._last_run:
            return self._cached_result
        """
        soil_drainage_mm: passed in from soil_moisture agent's excess
        drainage (precip - ET - runoff, when positive).
        """
        if soil_drainage_mm is None:
            soil_drainage_mm = self._estimate_drainage(year, month)

        recharge = max(0.0, soil_drainage_mm) * self.recharge_fraction

        # linear reservoir recession
        self.storage_mm = (self.storage_mm * self.recession_constant) + recharge

        # baseflow released this month = storage * (1 - recession_constant)
        released_mm = self.storage_mm * (1 - self.recession_constant)

        # convert mm to m³/s
        basin_area_m2 = self.basin_area_km2 * 1e4
        days = pd.Timestamp(year=year, month=month, day=1).days_in_month
        contribution_m3s = (released_mm / 1000 * basin_area_m2) / (days * 86400)

        self._cached_result = {
            "contribution_m3s": contribution_m3s,
            "uncertainty_pct": 0.15,
            "state": {"storage_mm": self.storage_mm, "recharge_mm": recharge}
        }
        self._last_run = (year, month)
        return self._cached_result

    def _estimate_drainage(self, year, month):
        # fallback: use precipitation as a rough proxy for drainage
        precip = self._get_var("precip_mm", year, month)
        return precip * 0.25 if not pd.isna(precip) else 0.0
