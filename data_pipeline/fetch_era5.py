import pandas as pd
import numpy as np
import os
import xarray as xr

# Mocking CDSAPI because it requires credentials
try:
    import cdsapi
    HAS_CDSAPI = True
except ImportError:
    HAS_CDSAPI = False

RAW_DATA_DIR = "data/raw"

def fetch_era5_maule(year_start=1960, year_end=2024):
    """
    In a real environment, this would call the CDS API.
    Here we handle missing credentials and provide mock data.
    """
    output_path = os.path.join(RAW_DATA_DIR, "era5_maule.csv")

    # Check for ~/.cdsapirc
    if HAS_CDSAPI and os.path.exists(os.path.expanduser("~/.cdsapirc")):
        try:
            c = cdsapi.Client()
            nc_path = os.path.join(RAW_DATA_DIR, "era5_maule.nc")
            c.retrieve(
                "reanalysis-era5-single-levels-monthly-means",
                {
                    "product_type": "monthly_averaged_reanalysis",
                    "variable": ["total_precipitation", "2m_temperature"],
                    "year": [str(y) for y in range(year_start, year_end + 1)],
                    "month": [f"{m:02d}" for m in range(1, 13)],
                    "time": "00:00",
                    "area": [-34, -71, -36, -69],  # N, W, S, E
                    "format": "netcdf"
                },
                nc_path
            )

            ds = xr.open_dataset(nc_path)
            # Variables often named 'tp' and 't2m'
            precip = ds["tp"].mean(dim=["latitude","longitude"]) * 1000  # m → mm
            temp = ds["t2m"].mean(dim=["latitude","longitude"]) - 273.15  # K → C

            df = pd.DataFrame({
                "date": pd.to_datetime(precip.time.values),
                "precip_mm": precip.values,
                "temp_c": temp.values
            })
            df["date"] = df["date"].dt.to_period("M").dt.to_timestamp()
            df.to_csv(output_path, index=False)
            return df
        except Exception as e:
            print(f"CDS API Error: {e}. Falling back to mock data.")
    else:
        print("CDS API credentials not found. Generating mock ERA5 data.")

    return generate_mock_era5_data(year_start, year_end, output_path)

def generate_mock_era5_data(year_start, year_end, output_path):
    dates = pd.date_range(start=f"{year_start}-01-01", end=f"{year_end}-12-01", freq="MS")
    np.random.seed(44)

    # Precip: Higher in winter (May-Aug in Southern Hemisphere)
    seasonal_precip = 100 * np.sin(2 * np.pi * (dates.month - 4) / 12) + 120
    precip = np.maximum(0, seasonal_precip + np.random.normal(0, 50, len(dates)))

    # Temp: Higher in summer (Dec-Feb)
    seasonal_temp = 10 * np.sin(2 * np.pi * (dates.month - 10) / 12) + 15
    temp = seasonal_temp + np.random.normal(0, 2, len(dates))

    df = pd.DataFrame({
        "date": dates,
        "precip_mm": precip,
        "temp_c": temp
    })
    df.to_csv(output_path, index=False)
    return df

def main():
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    fetch_era5_maule()
    print(f"ERA5 data saved to {os.path.join(RAW_DATA_DIR, 'era5_maule.csv')}")

if __name__ == "__main__":
    main()
