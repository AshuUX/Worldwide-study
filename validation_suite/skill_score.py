import pandas as pd
import numpy as np
from hydrology_engine.runner import HydrologyRunner
from hydrology_engine.baseline import compute_baseline
import json

def compute_metrics(actuals, predictions, baseline_preds):
    rmse_swarm = np.sqrt(np.mean((predictions - actuals) ** 2))
    rmse_baseline = np.sqrt(np.mean((baseline_preds - actuals) ** 2))
    skill_score = (1 - rmse_swarm / (rmse_baseline + 1e-9)) * 100
    return rmse_baseline, rmse_swarm, skill_score

def compute_skill_score():
    data = pd.read_csv("data/clean/maule_master.csv", parse_dates=["date"])
    baseline = compute_baseline(data)
    runner = HydrologyRunner()

    # Define periods
    train_mask = (data["date"] >= "2019-04-01") & (data["date"] <= "2021-12-01")
    test_mask = (data["date"] >= "2022-01-01") & (data["date"] <= "2022-12-01")

    train_data = data[train_mask].copy()
    test_data = data[test_mask].copy()

    results = {}

    for period_name, period_df in [("TRAIN", train_data), ("TEST", test_data)]:
        actuals = []
        swarm_preds = []
        baseline_preds = []
        seasonal_data = {
            "Spring": {"actual": [], "swarm": []},
            "Summer": {"actual": [], "swarm": []},
            "Autumn": {"actual": [], "swarm": []},
            "Winter": {"actual": [], "swarm": []}
        }

        def get_season(month):
            if month in [9, 10, 11]: return "Spring"
            if month in [12, 1, 2]: return "Summer"
            if month in [3, 4, 5]: return "Autumn"
            return "Winter"

        for _, row in period_df.iterrows():
            year, month = row["date"].year, row["date"].month
            actual = row["flow_m3s"]
            if pd.isna(actual): continue

            bl_pred = baseline[baseline["month"] == month]["mean_m3s"].iloc[0]
            swarm_res = runner.run(year, month)
            swarm_pred = swarm_res["p50"]

            actuals.append(actual)
            swarm_preds.append(swarm_pred)
            baseline_preds.append(bl_pred)

            season = get_season(month)
            seasonal_data[season]["actual"].append(actual)
            seasonal_data[season]["swarm"].append(swarm_pred)

        actuals = np.array(actuals)
        swarm_preds = np.array(swarm_preds)
        baseline_preds = np.array(baseline_preds)

        rmse_bl, rmse_sw, skill = compute_metrics(actuals, swarm_preds, baseline_preds)

        biases = {}
        for season, vals in seasonal_data.items():
            if vals["swarm"] and np.mean(vals["swarm"]) > 0:
                biases[season] = np.mean(vals["actual"]) / np.mean(vals["swarm"])
            else:
                biases[season] = np.nan

        results[period_name] = {
            "baseline_rmse": float(rmse_bl),
            "swarm_rmse": float(rmse_sw),
            "skill_score": float(skill),
            "biases": biases
        }

    print("RAW OUTPUT FOR SKILL SCORE:")
    print(json.dumps(results, indent=2))
    return results

if __name__ == "__main__":
    compute_skill_score()
