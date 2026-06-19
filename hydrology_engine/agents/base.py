import pandas as pd
import numpy as np

class HydrologyAgent:
    def __init__(self, data: pd.DataFrame, basin: str):
        self.data = data      # full clean dataframe
        self.basin = basin    # e.g. "maule"
        self.name = "base"

    def step(self, year: int, month: int) -> dict:
        """
        Returns dict with:
        - contribution_m3s: float — this agent's contribution to monthly mean flow
        - uncertainty_pct: float — agent's own uncertainty as % of contribution
        - state: dict — any state variables for interaction layer
        """
        raise NotImplementedError

    def _get_var(self, col, year, month):
        mask = (self.data["date"].dt.year == year) & (self.data["date"].dt.month == month)
        vals = self.data.loc[mask, col]
        return vals.iloc[0] if len(vals) > 0 else np.nan

    def _get_index(self, col, year, month):
        return self._get_var(col, year, month)

    def _rolling_mean(self, col, year, month, window=12):
        target_date = pd.Timestamp(year=year, month=month, day=1)
        mask = (self.data["date"] <= target_date)
        subset = self.data.loc[mask, col].tail(window)
        return subset.mean()

    def _climatological_mean(self, col, month, start_year=1981, end_year=2010):
        mask = (self.data["date"].dt.month == month) & \
               (self.data["date"].dt.year >= start_year) & \
               (self.data["date"].dt.year <= end_year)
        return self.data.loc[mask, col].mean()
