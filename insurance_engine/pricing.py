def illustrative_premium(trigger_result: dict, payout_usd: float,
                          calibration_error: float) -> dict:
    """
    Computes illustrative premium range.
    """
    results = {}

    for threshold_key, trigger in trigger_result.items():
        # pure premiums
        pure_premium_binary = trigger["binary_expected_loss_frac"] * payout_usd

        # uncertainty loading = calibration error × 1.5 × pure premium
        uncertainty_load = calibration_error * 1.5 * pure_premium_binary

        # risk margin = 25% of pure premium
        risk_margin = 0.25 * pure_premium_binary

        # expense loading = 15% of (pure + uncertainty + risk)
        subtotal = pure_premium_binary + uncertainty_load + risk_margin
        expense_load = 0.15 * subtotal

        total_premium = subtotal + expense_load
        premium_rate = total_premium / payout_usd if payout_usd > 0 else 0

        results[threshold_key] = {
            "pure_premium_usd": round(pure_premium_binary, 0),
            "total_premium_usd": round(total_premium, 0),
            "premium_rate_pct": round(premium_rate * 100, 2),
            "payout_usd": payout_usd,
            "return_period_years": trigger["return_period_years"],
            "NOTE": "ILLUSTRATIVE ONLY — not investable pricing"
        }

    return results
