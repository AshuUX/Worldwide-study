import numpy as np
import pandas as pd
from scipy.special import gamma
from .base import HydrologyAgent

class RoutingAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "routing"

    def step(self, year, month):
        # Simplified for monthly step: returns lag parameter
        return {"lag_months": 0.8, "uncertainty_pct": 0.10, "state": {}}

    @staticmethod
    def route(inflow_series_m3s, n=3, K_days=8):
        """
        Nash cascade unit hydrograph aggregated to monthly steps.
        This simplified retrofit smooths month-to-month transitions.
        """
        from scipy.special import gamma
        dt = 30  # days per month
        # Create daily IUH for up to 3 months (90 days)
        t_daily = np.arange(1, 91)
        iuh_daily = (t_daily**(n-1) * np.exp(-t_daily/K_days)) / (K_days**n * gamma(n))
        iuh_daily = iuh_daily / iuh_daily.sum()

        # Aggregate daily IUH to monthly weights
        # w0: fraction of current month's inflow reaching station in the same month
        # w1: fraction of previous month's inflow reaching station in the current month
        # ...
        w0 = np.sum(iuh_daily[0:30])
        w1 = np.sum(iuh_daily[30:60])
        w2 = np.sum(iuh_daily[60:90])
        weights = np.array([w0, w1, w2])
        weights = weights / weights.sum() # Ensure mass balance

        inflow = np.array(inflow_series_m3s)
        # Apply weights manually for the last month in history
        # (Equivalent to a monthly convolution)
        if len(inflow) == 1:
            return inflow * w0
        elif len(inflow) == 2:
            return np.array([inflow[0]*w0, inflow[1]*w0 + inflow[0]*w1])
        else:
            # For the last element:
            out_last = inflow[-1]*w0 + inflow[-2]*w1 + inflow[-3]*w2
            return np.append(inflow[:-1], out_last)
