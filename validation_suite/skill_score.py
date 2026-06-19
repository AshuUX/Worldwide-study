import pandas as pd
import numpy as np
from hydrology_engine.runner import HydrologyRunner
from hydrology_engine.baseline import compute_baseline

def compute_skill_score():
    data = pd.read_csv("data/clean/maule_master.csv", parse_dates=["date"])
    baseline = compute_baseline(data)
    runner = HydrologyRunner()

    # evaluate on 2006-2024 holdout
    holdout = data[data["date"].dt.year >= 2006].copy()

    baseline_errors = []
    swarm_errors = []

    for _, row in holdout.iterrows():
        year, month = row["date"].year, row["date"].month
        actual = row["flow_m3s"]
        if pd.isna(actual): continue

        baseline_pred = baseline[baseline["month"] == month]["mean_m3s"].iloc[0]
        baseline_errors.append((baseline_pred - actual) ** 2)

        swarm_result = runner.run(year=year, month=month)
        swarm_pred = swarm_result["p50"]
        swarm_errors.append((swarm_pred - actual) ** 2)

    baseline_rmse = np.sqrt(np.mean(baseline_errors))
    swarm_rmse = np.sqrt(np.mean(swarm_errors))
    skill_score = (1 - swarm_rmse / baseline_rmse) * 100

    result = {
        "baseline_rmse": float(baseline_rmse),
        "swarm_rmse": float(swarm_rmse),
        "skill_score": float(skill_score),
        "PASS": bool(skill_score >= 5.0)
    }

    print(result)
    return result

if __name__ == "__main__":
    compute_skill_score()
