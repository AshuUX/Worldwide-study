import numpy as np
from scipy import stats

def flow_to_generation(flow_dist_result: dict, plant: dict) -> dict:
    """
    Converts monthly flow distribution to generation distribution.
    """
    RHO = 1000
    G = 9.81

    samples_flow = flow_dist_result["samples"]

    # clip flow to plant operational range
    q_turbine = np.clip(samples_flow, plant["min_flow_m3s"], plant["max_flow_m3s"])

    if plant["type"] == "storage":
        # Target 65% capacity factor but constrained by inflow
        inflow_ratio = np.mean(samples_flow) / plant["design_flow_m3s"]
        effective_cf = min(0.65, inflow_ratio * 0.80)
        generation_samples_gwh = np.full(
            len(samples_flow),
            plant["capacity_mw"] * effective_cf * 730 / 1000
        ) * (1 + np.random.normal(0, 0.08, len(samples_flow)))
    else:
        # run-of-river: follows flow directly
        power_samples_mw = (RHO * G * q_turbine * plant["head_m"] * plant["efficiency"]) / 1e6
        power_samples_mw = np.clip(power_samples_mw, 0, plant["capacity_mw"])
        days = 30
        generation_samples_gwh = power_samples_mw * days * 24 / 1000

    generation_samples_gwh = np.maximum(generation_samples_gwh, 0.01)
    shape, loc, scale = stats.lognorm.fit(generation_samples_gwh, floc=0)
    dist = stats.lognorm(s=shape, loc=loc, scale=scale)

    return {
        "distribution": dist,
        "samples": generation_samples_gwh,
        "p10_gwh": dist.ppf(0.10),
        "p50_gwh": dist.ppf(0.50),
        "p90_gwh": dist.ppf(0.90),
        "mean_gwh": generation_samples_gwh.mean(),
        "plant_name": plant["name"]
    }
