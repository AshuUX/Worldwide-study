import pandas as pd
import numpy as np
from hydrology_engine.runner import HydrologyRunner
from hydrology_engine.baseline import compute_baseline

def compute_skill_score():
    data = pd.read_csv("data/clean/maule_master.csv", parse_dates=["date"])
    baseline = compute_baseline(data)
    runner = HydrologyRunner()

    # evaluate on period with real data
    holdout = data[(data["date"] >= "2019-04-01") & (data["date"] <= "2022-12-01")].copy()

    baseline_errors = []
    swarm_errors = []

    # Track seasonal errors for bias reporting
    seasonal_data = {
        "Spring": {"actual": [], "swarm": []}, # Sep, Oct, Nov
        "Summer": {"actual": [], "swarm": []}, # Dec, Jan, Feb
        "Autumn": {"actual": [], "swarm": []}, # Mar, Apr, May
        "Winter": {"actual": [], "swarm": []}  # Jun, Jul, Aug
    }

    def get_season(month):
        if month in [9, 10, 11]: return "Spring"
        if month in [12, 1, 2]: return "Summer"
        if month in [3, 4, 5]: return "Autumn"
        return "Winter"

    for _, row in holdout.iterrows():
        year, month = row["date"].year, row["date"].month
        actual = row["flow_m3s"]
        if pd.isna(actual): continue

        baseline_pred = baseline[baseline["month"] == month]["mean_m3s"].iloc[0]
        baseline_errors.append((baseline_pred - actual) ** 2)

        swarm_result = runner.run(year=year, month=month)
        swarm_pred = swarm_result["p50"]
        swarm_errors.append((swarm_pred - actual) ** 2)

        season = get_season(month)
        seasonal_data[season]["actual"].append(actual)
        seasonal_data[season]["swarm"].append(swarm_pred)

    baseline_rmse = np.sqrt(np.mean(baseline_errors))
    swarm_rmse = np.sqrt(np.mean(swarm_errors))
    skill_score = (1 - swarm_rmse / baseline_rmse) * 100

    # Calculate seasonal bias: mean(actual) / mean(swarm)
    biases = {}
    for season, vals in seasonal_data.items():
        if vals["swarm"]:
            biases[season] = np.mean(vals["actual"]) / np.mean(vals["swarm"])
        else:
            biases[season] = np.nan

    result = {
        "baseline_rmse": float(baseline_rmse),
        "swarm_rmse": float(swarm_rmse),
        "skill_score": float(skill_score),
        "seasonal_biases": biases,
        "PASS": bool(skill_score >= 5.0)
    }

    import json
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    compute_skill_score()
