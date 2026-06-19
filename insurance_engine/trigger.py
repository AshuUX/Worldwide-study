import numpy as np

def design_trigger(generation_dist_results: list, plant: dict,
                   threshold_pcts: list = [0.70, 0.80, 0.90]) -> dict:
    """
    Designs parametric trigger for a plant.
    """
    historical_mean_annual_gwh = plant["historical_mean_annual_gwh"]

    # simulate 2000 annual generation outcomes by summing 12 monthly distributions
    n_samples = 2000
    annual_samples = np.zeros(n_samples)
    for month_result in generation_dist_results:
        annual_samples += np.random.choice(month_result["samples"], n_samples, replace=True)

    triggers = {}
    for threshold_pct in threshold_pcts:
        trigger_gwh = historical_mean_annual_gwh * threshold_pct
        breach_probability = np.mean(annual_samples < trigger_gwh)

        # 1. Binary
        binary_expected_loss = breach_probability

        # 2. Proportional
        shortfalls = np.maximum(0, trigger_gwh - annual_samples)
        proportional_expected_loss_frac = np.mean(shortfalls) / trigger_gwh if trigger_gwh > 0 else 0

        triggers[f"threshold_{int(threshold_pct*100)}pct"] = {
            "trigger_gwh": trigger_gwh,
            "threshold_pct": threshold_pct,
            "breach_probability": breach_probability,
            "return_period_years": 1 / breach_probability if breach_probability > 0 else np.inf,
            "binary_expected_loss_frac": binary_expected_loss,
            "proportional_expected_loss_frac": proportional_expected_loss_frac,
        }

    return triggers
