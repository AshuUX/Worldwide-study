import pandas as pd
import numpy as np

def compute_baseline(data: pd.DataFrame, basin: str = "maule") -> pd.DataFrame:
    """
    Naive baseline: for each calendar month, compute mean ± std of historical flow.
    Training period: 1960-2005.
    """
    train = data[(data["date"].dt.year <= 2005)].copy()
    train["month"] = train["date"].dt.month

    baseline = train.groupby("month")["flow_m3s"].agg(
        mean_m3s="mean",
        std_m3s="std",
        p10=lambda x: np.percentile(x, 10) if len(x) > 0 else 0,
        p50=lambda x: np.percentile(x, 50) if len(x) > 0 else 0,
        p90=lambda x: np.percentile(x, 90) if len(x) > 0 else 0
    ).reset_index()

    return baseline
