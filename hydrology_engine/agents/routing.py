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
        dt = 30
        t = np.arange(1, len(inflow_series_m3s) * dt + 1)
        iuh = (t**(n-1) * np.exp(-t/K_days)) / (K_days**n * gamma(n))
        iuh = iuh / iuh.sum()
        outflow = np.convolve(inflow_series_m3s, iuh[:dt*2], mode="same")
        return outflow
