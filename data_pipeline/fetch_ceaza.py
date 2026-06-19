import pandas as pd
import numpy as np
import os

RAW_DATA_DIR = "data/raw"

def fetch_ceaza_snowpack(year_start=1960, year_end=2024):
    """
    Simulating snowpack data fetch from CR2/CEAZA.
    """
    output_path = os.path.join(RAW_DATA_DIR, "snowpack_maule.csv")
    print("Simulating snowpack data fetch.")
    return generate_mock_snowpack_data(year_start, year_end, output_path)

def generate_mock_snowpack_data(year_start, year_end, output_path):
    dates = pd.date_range(start=f"{year_start}-01-01", end=f"{year_end}-12-01", freq="MS")
    np.random.seed(46)

    # SWE peaks in late winter (Aug/Sep)
    seasonal_swe = 300 * np.sin(2 * np.pi * (dates.month - 4) / 12) + 250
    swe = np.maximum(0, seasonal_swe + np.random.normal(0, 100, len(dates)))

    # Snow covered area (km2) - Maule basin is ~20,300 km2
    sca = np.clip(swe * 20, 0, 20300)

    df = pd.DataFrame({
        "date": dates,
        "swe_mm": swe,
        "snow_covered_area_km2": sca
    })

    # Real data starts around 2000 for MODIS, maybe 1980s for some stations
    df.loc[df["date"].dt.year < 1985, ["swe_mm", "snow_covered_area_km2"]] = np.nan

    df.to_csv(output_path, index=False)
    return df

def main():
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    fetch_ceaza_snowpack()
    print(f"Snowpack data saved to {os.path.join(RAW_DATA_DIR, 'snowpack_maule.csv')}")

if __name__ == "__main__":
    main()
