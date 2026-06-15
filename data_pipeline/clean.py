import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
import logging

RAW_DATA_DIR = "data/raw"
CLEAN_DATA_DIR = "data/clean"

os.makedirs(CLEAN_DATA_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def fill_discharge_from_precip(df):
    """
    When discharge has gap > 3 months, estimate from ERA5 precip.
    """
    df = df.copy()
    # add 1-month and 2-month lagged precip as features
    df["precip_lag1"] = df["precip_mm"].shift(1)
    df["precip_lag2"] = df["precip_mm"].shift(2)
    # also add month-of-year as cyclical feature
    df["month_sin"] = np.sin(2 * np.pi * df["date"].dt.month / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["date"].dt.month / 12)

    features = ["precip_mm", "precip_lag1", "precip_lag2", "temp_c", "month_sin", "month_cos"]

    # Train on non-NaN discharge and features
    train_mask = df["flow_m3s"].notna() & df[features].notna().all(axis=1)
    if train_mask.sum() < 24:
        logging.warning("Not enough data to train discharge-precip regression.")
        return df, 0

    train = df[train_mask]
    X_train = train[features]
    y_train = train["flow_m3s"]

    model = LinearRegression()
    model.fit(X_train, y_train)
    r2 = model.score(X_train, y_train)

    # fill gaps
    gap_mask = df["flow_m3s"].isna() & df[features].notna().all(axis=1)
    if gap_mask.any():
        df.loc[gap_mask, "flow_m3s"] = model.predict(df.loc[gap_mask, features])
        df.loc[gap_mask, "flow_source"] = "era5_regression"
        logging.info(f"Filled {gap_mask.sum()} months of discharge using regression (R²={r2:.2f})")

    return df, r2

def clean_data():
    # 1. Load all raw files
    dga = pd.read_csv(os.path.join(RAW_DATA_DIR, "dga_discharge.csv"), parse_dates=["date"])
    noaa = pd.read_csv(os.path.join(RAW_DATA_DIR, "climate_indices.csv"), parse_dates=["date"])
    era5 = pd.read_csv(os.path.join(RAW_DATA_DIR, "era5_maule.csv"), parse_dates=["date"])
    snow = pd.read_csv(os.path.join(RAW_DATA_DIR, "snowpack_maule.csv"), parse_dates=["date"])
    # CNE generation is plant-specific, we'll keep it separate or handle it carefully

    # 2. Merge variables into one master dataframe
    master = era5.merge(dga[["date", "flow_m3s"]], on="date", how="left")
    master = master.merge(noaa, on="date", how="left")
    master = master.merge(snow[["date", "swe_mm"]], on="date", how="left")

    master = master.sort_values("date").reset_index(drop=True)
    master["flow_source"] = "dga_observed"
    master.loc[master["flow_m3s"].isna(), "flow_source"] = "missing"

    # 3. Gap-filling rules
    # Gaps ≤ 3 months: linear interpolation
    master["flow_m3s"] = master["flow_m3s"].interpolate(method="linear", limit=3)

    # Gaps > 3 months in discharge: ERA5 precipitation regression fallback
    master, r2 = fill_discharge_from_precip(master)

    # Gaps > 3 months in climate indices: flag as NaN (already NaN), log warning
    for col in ["enso_mei", "pdo_index", "aao_index"]:
        if master[col].isna().any():
            gaps = master[col].isna().sum()
            logging.warning(f"{col} has {gaps} missing months.")

    # 4. Standardisation verify (all done in fetch files)

    # 5. Write master
    master.to_csv(os.path.join(CLEAN_DATA_DIR, "maule_master.csv"), index=False)
    logging.info("Master clean data saved.")

if __name__ == "__main__":
    clean_data()
