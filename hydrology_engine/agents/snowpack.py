import numpy as np
import pandas as pd
from .base import HydrologyAgent

class SnowpackAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "snowpack"
        # Degree-day factor for Andes
        self.ddf_mm_per_degC_per_day = 4.5
        # Maule basin hypsometric curve
        self.elevation_bands = {
            "low":    {"elev_m": 1500, "area_frac": 0.25, "melt_threshold_c": 1.0},
            "mid":    {"elev_m": 2500, "area_frac": 0.45, "melt_threshold_c": 0.0},
            "high":   {"elev_m": 3500, "area_frac": 0.25, "melt_threshold_c": -1.0},
            "alpine": {"elev_m": 4500, "area_frac": 0.05, "melt_threshold_c": -2.0},
        }
        self.lapse_rate = -0.0065
        self.basin_ref_elev_m = 500

    def step(self, year: int, month: int) -> dict:
        temp_ref = self._get_var("temp_c", year, month)

        # get prior month SWE
        prior_date = pd.Timestamp(year=year, month=month, day=1) - pd.DateOffset(months=1)
        swe = self._get_var("swe_mm", prior_date.year, prior_date.month)

        if pd.isna(swe):
            swe = self._estimate_swe_from_precip(year, month)

        total_melt_mm = 0.0
        days_in_month = pd.Timestamp(year=year, month=month, day=1).days_in_month

        for band_name, band in self.elevation_bands.items():
            elev_diff = band["elev_m"] - self.basin_ref_elev_m
            temp_at_band = temp_ref + (self.lapse_rate * elev_diff)

            if temp_at_band > band["melt_threshold_c"]:
                # Potential melt depth in this band (mm)
                pot_melt_depth = self.ddf_mm_per_degC_per_day * (temp_at_band - band["melt_threshold_c"]) * days_in_month

                # Logic: swe is the basin-average depth.
                # We assume this depth is uniformly available for melting across all bands.
                # Mass balance: total_melt = sum(melt_depth_band * area_frac_band) <= total_swe
                melt_depth = min(pot_melt_depth, swe)
                total_melt_mm += melt_depth * band["area_frac"]

        # Final mass balance check: cannot melt more than available basin-avg SWE
        total_melt_mm = min(total_melt_mm, swe)

        basin_area_m2 = 203.0 * 1e6 # 1% of total basin for high-Andean snowpack
        contribution_m3s = (total_melt_mm / 1000 * basin_area_m2) / (days_in_month * 86400)

        return {
            "contribution_m3s": contribution_m3s,
            "uncertainty_pct": 0.20 if pd.isna(self._get_var("swe_mm", year, month)) else 0.12,
            "state": {"swe_mm": swe, "melt_mm": total_melt_mm}
        }

    def _estimate_swe_from_precip(self, year, month):
        swe = 0.0
        for m in range(4, month + 1):
            t = self._get_var("temp_c", year, m)
            p = self._get_var("precip_mm", year, m)
            if not pd.isna(t) and not pd.isna(p) and t < 2.0:
                swe += p * 0.7
        return swe
