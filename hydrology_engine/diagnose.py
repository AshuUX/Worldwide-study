"""
diagnose.py — prints every intermediate value in the flow calculation
for a single month, so we can manually verify each step against
physically reasonable magnitudes.

Run: python hydrology_engine/diagnose.py --year 2015 --month 7
"""
import argparse
import pandas as pd
import numpy as np
import os
import sys

# Add root to sys.path
sys.path.append(os.getcwd())

def diagnose(year, month, data):
    print(f"\n{'='*70}")
    print(f"DIAGNOSTIC RUN: {year}-{month:02d}")
    print(f"{'='*70}\n")

    # ---- RAW INPUT DATA ----
    print("--- RAW INPUT DATA ---")
    row = data[(data["date"].dt.year == year) & (data["date"].dt.month == month)]
    if row.empty:
        print(f"NO DATA FOUND for {year}-{month:02d} — STOP HERE, this is the bug")
        return
    print(f"precip_mm:        {row['precip_mm'].values[0]:.2f}")
    print(f"temp_c:           {row['temp_c'].values[0]:.2f}")
    print(f"enso_mei:         {row.get('enso_mei', pd.Series([np.nan])).values[0]}")
    print(f"snowpack_swe:     {row.get('swe_mm', pd.Series([np.nan])).values[0]}") # Note: col name is swe_mm
    print(f"actual_flow_m3s:  {row.get('flow_m3s', pd.Series([np.nan])).values[0]} (GROUND TRUTH)")

    # ---- EACH AGENT, RAW OUTPUT, NO NOISE ----
    print("\n--- AGENT OUTPUTS (no noise, single deterministic call) ---")

    from hydrology_engine.agents.enso import ENSOAgent
    from hydrology_engine.agents.snowpack import SnowpackAgent
    from hydrology_engine.agents.pdo import PDOAgent
    from hydrology_engine.agents.aao import AAOAgent
    from hydrology_engine.agents.glacier import GlacierAgent
    from hydrology_engine.agents.soil_moisture import SoilMoistureAgent
    from hydrology_engine.agents.puelche import PuelcheAgent
    from hydrology_engine.agents.baseflow import BaseflowAgent
    from hydrology_engine.agents.reservoir import ReservoirAgent
    from hydrology_engine.agents.precip_anomaly import PrecipAnomalyAgent

    agents = {
        "enso": ENSOAgent(data, "maule"),
        "snowpack": SnowpackAgent(data, "maule"),
        "pdo": PDOAgent(data, "maule"),
        "aao": AAOAgent(data, "maule"),
        "glacier": GlacierAgent(data, "maule"),
        "soil_moisture": SoilMoistureAgent(data, "maule"),
        "puelche": PuelcheAgent(data, "maule"),
        "baseflow": BaseflowAgent(data, "maule"),
        "reservoir": ReservoirAgent(data, "maule"),
        "precip_anomaly": PrecipAnomalyAgent(data, "maule"),
    }

    outputs = {}
    for name, agent in agents.items():
        result = agent.step(year, month)
        outputs[name] = result
        print(f"\n  [{name}]")
        for k, v in result.items():
            if k != "state":
                print(f"    {k}: {v}")
        if "state" in result:
            print(f"    state: {result['state']}")

    # ---- SOIL MOISTURE / RUNOFF SPECIFIC SANITY CHECK ----
    print("\n--- RUNOFF FRACTION SANITY CHECK ---")
    runoff_frac = outputs["soil_moisture"].get("runoff_fraction", None)
    precip = row['precip_mm'].values[0]
    print(f"  precip_mm: {precip:.2f}")
    print(f"  runoff_fraction: {runoff_frac}")
    print(f"  implied runoff_mm: {precip * runoff_frac if runoff_frac else 'N/A'}")
    if runoff_frac and runoff_frac > 0.6:
        print(f"  *** WARNING: runoff fraction {runoff_frac:.2f} is implausibly "
              f"high. Expected 0.2-0.4 for steep terrain. CHECK SCS-CN CALCULATION ***")

    # ---- INTERACTION LAYER, STEP BY STEP ----
    print("\n--- INTERACTION LAYER BREAKDOWN ---")
    from hydrology_engine.interaction import apply_interactions
    interaction_result = apply_interactions(outputs, year, month)
    print(f"  climate_multiplier: {interaction_result.get('climate_multiplier')}")
    print(f"  components: {interaction_result.get('components')}")
    print(f"  TOTAL RAW FLOW (m3/s): {interaction_result.get('total_flow_m3s')}")

    # ---- UNIT SANITY CHECKS ----
    print("\n--- UNIT SANITY CHECKS ---")
    total = interaction_result.get('total_flow_m3s', 0)
    actual = row.get('flow_m3s', pd.Series([np.nan])).values[0]
    print(f"  Model total flow:  {total:.2f} m3/s")
    print(f"  Actual flow:       {actual:.2f} m3/s")
    print(f"  Ratio (model/actual): {total/actual if actual else 'N/A':.2f}")

    if total > 0 and actual > 0:
        ratio = total / actual
        if ratio > 5 or ratio < 0.2:
            print(f"  *** SEVERE MISMATCH — ratio of {ratio:.2f}x suggests a "
                  f"UNIT CONVERSION ERROR somewhere (e.g. mm vs m, "
                  f"monthly total vs daily rate, km2 vs m2) ***")

    # ---- BASIN AREA CONSISTENCY CHECK ----
    print("\n--- BASIN AREA USED BY EACH AGENT (must all match) ---")
    print("  Check that every agent uses the SAME basin_area_km2 value.")
    # We can inspect the agents directly if they stored it
    for name, agent in agents.items():
        area = getattr(agent, 'basin_area_km2', getattr(agent, 'area_km2', getattr(agent, 'basin_area_m2', None)))
        if area:
            print(f"  {name}: {area}")

    return interaction_result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2015)
    parser.add_argument("--month", type=int, default=7)
    args = parser.parse_args()

    data_path = "data/clean/maule_master.csv"
    if not os.path.exists(data_path):
        print(f"ERROR: {data_path} not found. Run data pipeline first.")
        sys.exit(1)

    data = pd.read_csv(data_path, parse_dates=["date"])
    diagnose(args.year, args.month, data)
