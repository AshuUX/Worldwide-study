import numpy as np
from scipy import stats

def build_flow_distribution(year: int, month: int, agents: list,
                             interaction_fn, n_samples: int = 1000) -> dict:
    """
    Runs n_samples Monte Carlo iterations.
    Returns a fitted lognormal distribution.
    """
    samples = []

    for _ in range(n_samples):
        # run all agents
        agent_outputs = {}
        for agent in agents:
            result = agent.step(year, month)
            # add noise
            for key, val in result.items():
                if key in ("contribution_m3s", "contribution_multiplier", "runoff_fraction", "melt_accelerator", "precip_suppressor"):
                    noise_std = abs(val) * result.get("uncertainty_pct", 0.10)
                    result[key] = val + np.random.normal(0, noise_std)
            agent_outputs[agent.name] = result

        # apply interaction rules
        interaction_result = interaction_fn(agent_outputs, year, month)
        samples.append(max(0.01, interaction_result["total_flow_m3s"]))

    samples = np.array(samples)

    # fit lognormal distribution
    shape, loc, scale = stats.lognorm.fit(samples, floc=0)
    dist = stats.lognorm(s=shape, loc=loc, scale=scale)

    p10, p50, p90 = dist.ppf([0.10, 0.50, 0.90])

    return {
        "distribution": dist,
        "samples": samples,
        "p10": p10,
        "p50": p50,
        "p90": p90,
        "mean": samples.mean(),
        "std": samples.std(),
        "cv": samples.std() / (samples.mean() + 1e-6)
    }
