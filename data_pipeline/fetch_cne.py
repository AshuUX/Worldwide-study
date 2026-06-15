import pandas as pd
import numpy as np
import os

RAW_DATA_DIR = "data/raw"

def fetch_cne_generation(year_start=1960, year_end=2024):
    """
    In a real environment, this would download Excel files from CNE.
    """
    output_path = os.path.join(RAW_DATA_DIR, "cne_generation.csv")
    print("Simulating CNE data fetch.")
    return generate_mock_cne_data(year_start, year_end, output_path)

def generate_mock_cne_data(year_start, year_end, output_path):
    plants = [
        {"name": "Colbun", "capacity_mw": 400, "type": "storage"},
        {"name": "Machicura", "capacity_mw": 90, "type": "run_of_river"},
        {"name": "Isla", "capacity_mw": 68, "type": "run_of_river"},
        {"name": "San Ignacio", "capacity_mw": 40, "type": "run_of_river"}
    ]

    dates = pd.date_range(start=f"{year_start}-01-01", end=f"{year_end}-12-01", freq="MS")
    np.random.seed(45)

    records = []
    for plant in plants:
        for date in dates:
            # Generation follows a seasonal pattern similar to flow
            seasonal_factor = 0.4 * np.sin(2 * np.pi * (date.month - 7) / 12) + 0.5
            # Storage plants have more stable generation
            if plant["type"] == "storage":
                seasonal_factor = 0.2 * np.sin(2 * np.pi * (date.month - 7) / 12) + 0.6

            # Max possible GWh in a month = capacity * 24 * 30 / 1000
            max_gwh = plant["capacity_mw"] * 24 * 30 / 1000
            gen = max_gwh * seasonal_factor + np.random.normal(0, max_gwh * 0.1)
            gen = np.clip(gen, 0, max_gwh)

            records.append({
                "date": date,
                "plant_name": plant["name"],
                "capacity_mw": plant["capacity_mw"],
                "generation_gwh": gen
            })

    df = pd.DataFrame(records)
    # Filter by available years in CNE (usually more recent)
    df = df[df["date"].dt.year >= 1990]
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    fetch_cne_generation()
    print(f"CNE data saved to {os.path.join(RAW_DATA_DIR, 'cne_generation.csv')}")
