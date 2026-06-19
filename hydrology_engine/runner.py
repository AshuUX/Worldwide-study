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
from .interaction import apply_interactions
from .emergence import build_flow_distribution

class HydrologyRunner:
    def __init__(self, data_path="data/clean/maule_master.csv", basin="maule"):
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
            PrecipAnomalyAgent(self.data, basin)
        ]

    def run(self, year, month):
        return build_flow_distribution(year, month, self.agents, apply_interactions)

if __name__ == "__main__":
    runner = HydrologyRunner()
    result = runner.run(2021, 10)
    print(f"Oct 2021 Maule Flow P50: {result['p50']:.2f} m3/s")
