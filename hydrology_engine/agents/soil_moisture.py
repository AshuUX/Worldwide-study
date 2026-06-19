import numpy as np
import pandas as pd
from .base import HydrologyAgent

class SoilMoistureAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "soil_moisture"
        self.CN = {"dry": 55, "normal": 70, "wet": 82}
        self.max_storage_mm = 180
        self.current_storage_mm = 90

    def step(self, year, month):
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

        CN = self.CN[amc]
        S = (25400 / CN) - 254
        if precip > 0.2 * S:
            runoff_mm = (precip - 0.2 * S) ** 2 / (precip + 0.8 * S)
        else:
            runoff_mm = 0.0

        runoff_fraction = runoff_mm / precip if precip > 0 else 0.0

        return {
            "runoff_fraction": runoff_fraction,
            "contribution_m3s": 0.0,
            "uncertainty_pct": 0.15,
            "state": {
                "amc": amc,
                "storage_mm": self.current_storage_mm,
                "runoff_fraction": runoff_fraction,
                "storage_frac": storage_frac
            }
        }

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
