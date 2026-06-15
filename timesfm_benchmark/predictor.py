import numpy as np
import pandas as pd

try:
    import timesfm
    HAS_TIMESFM = True
except ImportError:
    HAS_TIMESFM = False

def run_timesfm(flow_series: pd.Series, forecast_horizon: int = 12) -> np.ndarray:
    """
    flow_series: monthly discharge in m³/s, DatetimeIndex
    Returns: array of point forecasts for next forecast_horizon months
    """
    if not HAS_TIMESFM:
        # Fallback for environment without timesfm
        print("Warning: timesfm not installed. Returning seasonal persistence forecast.")
        series_values = flow_series.values.astype(float)
        if len(series_values) >= 12:
            return series_values[-12: -12 + forecast_horizon]
        else:
            return np.full(forecast_horizon, series_values.mean())

    tfm = timesfm.TimesFm(
        context_len=240,   # 20 years of monthly data as context
        horizon_len=forecast_horizon,
        input_patch_len=32,
        output_patch_len=128,
        num_layers=20,
        model_dims=1280,
        backend="cpu"  # use "gpu" if available
    )
    tfm.load_from_checkpoint(repo_id="google/timesfm-1.0-200m")

    # TimesFM expects normalised input
    series_values = flow_series.values.astype(float)
    mean, std = series_values.mean(), series_values.std()
    normalised = (series_values - mean) / (std + 1e-6)

    forecast_normalised = tfm.forecast(
        inputs=[normalised],
        freq=[0]  # 0 = monthly frequency
    )[0]

    # denormalise
    forecast = (forecast_normalised * std) + mean
    return np.maximum(forecast, 0.0)[:forecast_horizon]
