import numpy as np
from scipy import stats

def build_flow_distribution(year: int, month: int, agents: list,
                             interaction_fn, n_samples: int = 100) -> dict:
    samples = []

    for _ in range(n_samples):
        agent_outputs = {}
        for agent in agents:
            # call step() fresh — agent.step() must return a NEW dict each call,
            # not a cached/mutated one
            result = agent.step(year, month)

            # build a clean copy with noise applied to NEW keys,
            # never overwrite the original deterministic value in place
            noisy_result = dict(result)  # shallow copy, breaks the mutation chain
            uncertainty = result.get("uncertainty_pct", 0.10)

            for key in ("contribution_m3s", "contribution_multiplier"):
                if key in result:
                    clean_val = result[key]
                    noise_std = abs(clean_val) * uncertainty
                    # sample noise fresh each iteration, write to a NEW dict
                    noisy_result[key] = clean_val + np.random.normal(0, noise_std)

            agent_outputs[agent.name] = noisy_result

        interaction_result = interaction_fn(agent_outputs, year, month)
        samples.append(max(0.01, interaction_result["total_flow_m3s"]))

    samples = np.array(samples)

    # SANITY CHECK — if std is more than 2x the mean, something is still
    # wrong upstream. Print a warning rather than silently fitting garbage.
    if samples.std() > 2 * samples.mean():
        print(f"WARNING: sample std ({samples.std():.1f}) exceeds 2x mean "
              f"({samples.mean():.1f}) for {year}-{month:02d}. "
              f"Distribution may be unstable.")

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
