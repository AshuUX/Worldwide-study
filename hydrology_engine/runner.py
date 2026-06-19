import pandas as pd
import os
from .agents.enso import ENSOAgent
from .agents.snowpack import SnowpackAgent
from .agents.pdo import PDOAgent
from .agents.aao import AAOAgent
from .agents.glacier import GlacierAgent
from .agents.soil_moisture import SoilMoistureAgent
from .agents.puelche import PuelcheAgent
from .agents.routing import RoutingAgent
from .agents.reservoir import ReservoirAgent
from .agents.precip_anomaly import PrecipAnomalyAgent
from .agents.baseflow import BaseflowAgent
from .interaction import apply_interactions
from .emergence import build_flow_distribution
from .agents.routing import RoutingAgent
import numpy as np

class HydrologyRunner:
    def __init__(self, data_path="data/clean/maule_master.csv", basin="maule"):
        if isinstance(data_path, pd.DataFrame):
             self.data = data_path
        else:
             self.data = pd.read_csv(data_path, parse_dates=["date"])
        self.basin = basin
        self.agents = [
            ENSOAgent(self.data, basin),
            SnowpackAgent(self.data, basin),
            PDOAgent(self.data, basin),
            AAOAgent(self.data, basin),
            GlacierAgent(self.data, basin),
            SoilMoistureAgent(self.data, basin),
            PuelcheAgent(self.data, basin),
            RoutingAgent(self.data, basin),
            ReservoirAgent(self.data, basin),
            PrecipAnomalyAgent(self.data, basin),
            BaseflowAgent(self.data, basin)
        ]
        self._raw_flow_history = []

    def run(self, year, month):
        raw_flow_result = build_flow_distribution(year, month, self.agents, apply_interactions)
        self._raw_flow_history.append(raw_flow_result["p50"])

        # apply routing once history is enough
        if len(self._raw_flow_history) >= 2:
            # simplified convolution on monthly data
            routed_series = RoutingAgent.route(np.array(self._raw_flow_history[-3:]), n=3, K_days=8)
            routing_adjustment = routed_series[-1] / self._raw_flow_history[-1]
        else:
            routing_adjustment = 1.0

        raw_flow_result["p10"] *= routing_adjustment
        raw_flow_result["p50"] *= routing_adjustment
        raw_flow_result["p90"] *= routing_adjustment
        raw_flow_result["samples"] = raw_flow_result["samples"] * routing_adjustment

        return raw_flow_result

if __name__ == "__main__":
    runner = HydrologyRunner()
    result = runner.run(2021, 10)
    print(f"Oct 2021 Maule Flow P50: {result['p50']:.2f} m3/s")
