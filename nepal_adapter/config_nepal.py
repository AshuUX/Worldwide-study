# All Nepal-specific parameters
BASIN_PARAMS = {
    "koshi": {
        "area_km2": 87_311,
        "glacier_area_km2": 4_668,
        "mean_elevation_m": 4_400,
        "elevation_bands": {
            "low":    {"elev_m": 2000, "area_frac": 0.15, "ddf": 4.0},
            "mid":    {"elev_m": 3500, "area_frac": 0.30, "ddf": 5.5},
            "high":   {"elev_m": 5000, "area_frac": 0.40, "ddf": 7.0},
            "alpine": {"elev_m": 6500, "area_frac": 0.15, "ddf": 9.0},
        }
    }
}

# IOD replaces PDO
IOD_TO_PRECIP_COEFF = +0.12  # positive IOD → increased monsoon precip Nepal

# MJO active phases 2, 3 → suppress Nepal monsoon
MJO_PHASE_MULTIPLIERS = {1: 1.0, 2: 0.85, 3: 0.80, 4: 0.95, 5: 1.05, 6: 1.20, 7: 1.15, 8: 1.05}

# Monsoon onset/withdrawal climatology
MONSOON_ONSET_MEAN_DOY = 165  # ~June 14
MONSOON_WITHDRAWAL_MEAN_DOY = 280  # ~Oct 7
MONSOON_ONSET_STD_DAYS = 12

KOSHI_PLANTS = [
    {"name": "Upper Tamakoshi", "capacity_mw": 456, "type": "storage", "historical_mean_annual_gwh": 2200},
    {"name": "Trishuli", "capacity_mw": 24, "type": "run_of_river", "historical_mean_annual_gwh": 160},
    {"name": "Sunkoshi", "capacity_mw": 10.05, "type": "run_of_river", "historical_mean_annual_gwh": 70}
]
