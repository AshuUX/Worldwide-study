import pandas as pd
import numpy as np
from hydrology_engine.runner import HydrologyRunner
from timesfm_benchmark.calibration import calibration_test

def run_calibration_test():
    data = pd.read_csv("data/clean/maule_master.csv", parse_dates=["date"])
    runner = HydrologyRunner()

    # Test on recent 5 years
    test_data = data[data["date"].dt.year >= 2019].tail(24)

    swarm_dists = []
    actuals = []

    for _, row in test_data.iterrows():
        year, month = row["date"].year, row["date"].month
        if pd.isna(row["flow_m3s"]): continue

        res = runner.run(year, month)
        swarm_dists.append(res)
        actuals.append(row["flow_m3s"])

    results = calibration_test(swarm_dists, np.array(actuals))
    print(results)
    return results

if __name__ == "__main__":
    run_calibration_test()
