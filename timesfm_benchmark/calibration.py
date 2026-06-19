import numpy as np

def calibration_test(swarm_distributions: list, actuals: np.ndarray) -> dict:
    """
    Tests whether confidence intervals are calibrated.
    For a well-calibrated model:
    - 50% of actuals should fall within P25-P75
    - 80% of actuals should fall within P10-P90
    - 90% of actuals should fall within P05-P95
    """
    confidence_levels = [0.50, 0.80, 0.90, 0.95]
    results = {}

    # Ensure swarm_distributions and actuals have same length
    n = min(len(swarm_distributions), len(actuals))
    swarm_distributions = swarm_distributions[:n]
    actuals = actuals[:n]

    for cl in confidence_levels:
        lower_q = (1 - cl) / 2
        upper_q = 1 - lower_q
        inside = 0
        for dist_result, actual in zip(swarm_distributions, actuals):
            dist = dist_result["distribution"]
            lower = dist.ppf(lower_q)
            upper = dist.ppf(upper_q)
            if lower <= actual <= upper:
                inside += 1
        observed_coverage = inside / n if n > 0 else 0
        results[f"cl_{int(cl*100)}"] = {
            "expected": cl,
            "observed": observed_coverage,
            "calibration_error": abs(observed_coverage - cl)
        }

    overall_error = np.mean([v["calibration_error"] for v in results.values()])
    results["overall_calibration_error"] = overall_error

    return results
