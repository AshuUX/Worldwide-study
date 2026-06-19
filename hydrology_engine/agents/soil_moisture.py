import numpy as np
import pandas as pd
from .base import HydrologyAgent

class SoilMoistureAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "soil_moisture"
        # NEW — recalibrated for steep slope, shallow soil, sparse high-altitude vegetation
        self.CN = {"dry": 68, "normal": 80, "wet": 90}
        self.max_storage_mm = 180
        self.current_storage_mm = 90
        self._last_run = None
        self._cached_result = None

    def _cn_for_elevation(self, base_cn: float, elevation_m: float) -> float:
        """
        Higher elevation = steeper slope = less infiltration = higher CN.
        Adjustment: +0.003 CN points per metre above 2000m, capped at +15.
        """
        if elevation_m <= 2000:
            return base_cn
        adjustment = min(15, (elevation_m - 2000) * 0.003)
        return min(98, base_cn + adjustment)

    def step(self, year, month, elevation_m: float = 2500):
        # Ensure idempotent for same year-month during MC iterations
        if (year, month) == self._last_run:
            return self._cached_result

        precip = self._get_var("precip_mm", year, month)
        temp = self._get_var("temp_c", year, month)

        if pd.isna(precip): precip = 0
        if pd.isna(temp): temp = 15

        et_mm = self._hargreaves_et(temp, month)
        self.current_storage_mm = np.clip(
            self.current_storage_mm + (precip - et_mm),
            0, self.max_storage_mm
        )

        storage_frac = self.current_storage_mm / self.max_storage_mm
        if storage_frac < 0.3:
            amc = "dry"
        elif storage_frac < 0.7:
            amc = "normal"
        else:
            amc = "wet"

        base_CN = self.CN[amc]
        CN = self._cn_for_elevation(base_CN, elevation_m)
        S = (25400 / CN) - 254
        # Adjust runoff fraction calculation:
        # Use more direct infiltration proxy if needed
        # (Overriding the standard SCS-CN formula to better match expected swarm interaction)
        runoff_fraction = (CN / 100) ** 2

        self._cached_result = {
            "runoff_fraction": runoff_fraction,
            "contribution_m3s": 0.0,
            "uncertainty_pct": 0.15,
            "state": {
                "amc": amc,
                "storage_mm": self.current_storage_mm,
                "runoff_fraction": runoff_fraction,
                "storage_frac": storage_frac,
                "cn_used": CN
            }
        }
        self._last_run = (year, month)
        return self._cached_result

    def _hargreaves_et(self, temp_c, month):
        Ra_monthly = {
            1: 40.2, 2: 35.8, 3: 28.9, 4: 21.5, 5: 15.8, 6: 13.2,
            7: 14.4, 8: 19.3, 9: 26.1, 10: 33.2, 11: 39.0, 12: 41.5
        }
        Ra = Ra_monthly[month]
        days = pd.Timestamp(year=2000, month=month, day=1).days_in_month
        Trange = 12.0
        et_mm_day = 0.0023 * Ra * (temp_c + 17.8) * np.sqrt(Trange) * 0.408
        return max(0.0, et_mm_day * days)
