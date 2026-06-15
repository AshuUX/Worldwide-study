import numpy as np
import pandas as pd

def compute_basis_risk(model_outputs: list, cne_actuals: pd.DataFrame, plant_name: str) -> dict:
    """
    Compares model P50 generation against CNE reported actuals.
    """
    plant_actuals = cne_actuals[cne_actuals["plant_name"] == plant_name].copy()

    errors = []
    for _, row in plant_actuals.iterrows():
        model = next((m for m in model_outputs
                      if m["year"] == row["date"].year and m["month"] == row["date"].month), None)
        if model:
            # Avoid division by zero
            actual = row["generation_gwh"]
            if actual > 0:
                error_pct = (model["p50_gwh"] - actual) / actual * 100
                errors.append(error_pct)

    if not errors:
        return {"plant_name": plant_name, "rmse_pct": 0, "flag": "NO_DATA"}

    errors = np.array(errors)
    rmse_pct = np.sqrt(np.mean(errors**2))

    return {
        "plant_name": plant_name,
        "rmse_pct": rmse_pct,
        "mean_bias_pct": np.mean(errors),
        "max_error_pct": np.max(np.abs(errors)),
        "n_months": len(errors),
        "flag": "HIGH_BASIS_RISK" if rmse_pct > 20 else "ACCEPTABLE"
    }
