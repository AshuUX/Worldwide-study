import pytest
import numpy as np
from scipy import stats
from insurance_engine.trigger import design_trigger
from insurance_engine.pricing import illustrative_premium
from generation_translator.basis_risk import compute_basis_risk
import pandas as pd

def make_mock_distribution(mean_gwh, cv=0.25):
    sigma = np.sqrt(np.log(1 + cv**2))
    mu = np.log(mean_gwh) - sigma**2 / 2
    samples = np.random.lognormal(mu, sigma, 2000)
    shape, loc, scale = stats.lognorm.fit(samples, floc=0)
    dist = stats.lognorm(s=shape, loc=loc, scale=scale)
    return {"distribution": dist, "samples": samples, "p50_gwh": mean_gwh}

def test_trigger_breach_probability_sensible():
    monthly_dists = [make_mock_distribution(150) for _ in range(12)]
    plant = {
        "name": "TestPlant",
        "historical_mean_annual_gwh": 1800
    }
    triggers = design_trigger(monthly_dists, plant, threshold_pcts=[0.70, 0.80, 0.90])

    bp_70 = triggers["threshold_70pct"]["breach_probability"]
    bp_80 = triggers["threshold_80pct"]["breach_probability"]
    bp_90 = triggers["threshold_90pct"]["breach_probability"]

    assert bp_70 <= bp_80 <= bp_90

def test_pricing_outputs_note():
    # Increase variance to ensure some breach probability for testing premiums
    monthly_dists = [make_mock_distribution(150, cv=0.5) for _ in range(12)]
    plant = {"name": "TestPlant", "historical_mean_annual_gwh": 1800}
    # Use higher threshold to ensure breach probability > 0
    triggers = design_trigger(monthly_dists, plant, threshold_pcts=[0.95])
    pricing = illustrative_premium(triggers, payout_usd=5000000, calibration_error=0.12)

    for key, val in pricing.items():
        assert "ILLUSTRATIVE" in val["NOTE"]
        assert val["total_premium_usd"] > val["pure_premium_usd"]

def test_basis_risk_flags_high_error():
    model_outputs = [
        {"year": 2020, "month": m, "p50_gwh": 195}
        for m in range(1, 13)
    ]
    cne_actuals = pd.DataFrame([
        {"plant_name": "TestPlant", "date": pd.Timestamp(year=2020, month=m, day=1), "generation_gwh": 150}
        for m in range(1, 13)
    ])
    result = compute_basis_risk(model_outputs, cne_actuals, "TestPlant")
    assert result["flag"] == "HIGH_BASIS_RISK"
    assert result["rmse_pct"] > 20
