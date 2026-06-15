import pandas as pd
from hydrology_engine.runner import HydrologyRunner
from generation_translator.translator import flow_to_generation
import json

def validate_2021_drought():
    """
    Checks whether the model captures the 2021 Chilean megadrought.
    """
    runner = HydrologyRunner()

    with open("generation_translator/plants_chile.json", "r") as f:
        plants = json.load(f)["plants"]
    colbun_plant = next(p for p in plants if p["name"] == "Colbun")

    # Run model for 2021
    predictions_2021 = {}
    for month in range(1, 13):
        flow_dist = runner.run(year=2021, month=month)
        gen_dist = flow_to_generation(flow_dist, colbun_plant)
        predictions_2021[month] = {
            "flow": flow_dist,
            "generation": gen_dist
        }

    # Load actuals
    cne_actuals = pd.read_csv("data/raw/cne_generation.csv", parse_dates=["date"])
    colbun_actual_2021_gwh = cne_actuals[
        (cne_actuals["plant_name"] == "Colbun") &
        (cne_actuals["date"].dt.year == 2021)
    ]["generation_gwh"].sum()

    colbun_predicted_annual = sum(predictions_2021[m]["generation"]["p50_gwh"] for m in range(1, 13))
    colbun_p10_annual = sum(predictions_2021[m]["generation"]["p10_gwh"] for m in range(1, 13))
    colbun_p90_annual = sum(predictions_2021[m]["generation"]["p90_gwh"] for m in range(1, 13))

    captured = colbun_p10_annual <= colbun_actual_2021_gwh <= colbun_p90_annual
    p50_error_pct = abs(colbun_predicted_annual - colbun_actual_2021_gwh) / colbun_actual_2021_gwh * 100

    result = {
        "colbun_actual_2021_gwh": float(colbun_actual_2021_gwh),
        "colbun_predicted_p50_gwh": float(colbun_predicted_annual),
        "colbun_p10_gwh": float(colbun_p10_annual),
        "colbun_p90_gwh": float(colbun_p90_annual),
        "actual_captured_in_p10_p90": bool(captured),
        "p50_error_pct": float(p50_error_pct),
        "PASS": bool(captured and p50_error_pct < 25.0)
    }

    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    validate_2021_drought()
