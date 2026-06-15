import numpy as np
from hydrology_engine.agents.base import HydrologyAgent

class IODAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "iod"
        self.iod_to_precip_coeff = 0.12

    def step(self, year, month):
        # In Nepal, IOD is important. Positive IOD -> more rain.
        # Mocking IOD index for now
        iod_val = np.random.normal(0, 0.5)
        flow_multiplier = 1.0 + (self.iod_to_precip_coeff * iod_val)
        return {
            "contribution_multiplier": np.clip(flow_multiplier, 0.7, 1.3),
            "uncertainty_pct": 0.10,
            "state": {"iod_value": iod_val}
        }

class MonsoonOnsetAgent(HydrologyAgent):
    def __init__(self, data, basin):
        super().__init__(data, basin)
        self.name = "monsoon_onset"
        self.normal_doy = 165

    def step(self, year, month):
        if month not in {6, 7}:
             return {"contribution_multiplier": 1.0, "uncertainty_pct": 0.05, "state": {}}

        # each day early onset → +0.8% June-July flow
        onset_diff = np.random.normal(0, 10) # deviation in days
        flow_multiplier = 1.0 - (onset_diff * 0.008)
        return {
            "contribution_multiplier": np.clip(flow_multiplier, 0.8, 1.2),
            "uncertainty_pct": 0.10,
            "state": {"onset_diff": onset_diff}
        }
