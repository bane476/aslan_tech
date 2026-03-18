import math
from datetime import date

from sqlalchemy.orm import Session

from app.data_access import load_domestic_metric_series


def _linear_regression(values: list[float]) -> tuple[float, float]:
    if len(values) < 2:
        return 0.0, values[-1] if values else 0.0
    x_values = list(range(len(values)))
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(values) / len(values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    slope = numerator / denominator if denominator else 0.0
    intercept = y_mean - (slope * x_mean)
    return slope, intercept


def _residual_std(values: list[float], slope: float, intercept: float) -> float:
    if len(values) < 3:
        return max(values[-1] * 0.05, 1.0) if values else 1.0
    residuals = []
    for index, value in enumerate(values):
        expected = (slope * index) + intercept
        residuals.append(value - expected)
    variance = sum(item * item for item in residuals) / max(len(residuals) - 1, 1)
    return math.sqrt(variance)


def forecast_lpg_demand(db: Session, horizon_days: int) -> dict:
    series = load_domestic_metric_series(db, "lpg_consumption")
    if not series:
        raise ValueError("No PPAC LPG consumption data is available. Run PPAC ingestion first.")

    values = [value for _, value in series][-24:]
    slope, intercept = _linear_regression(values)
    std_dev = _residual_std(values, slope, intercept)
    forecast_steps = 1 if horizon_days == 30 else 2
    start_index = len(values)
    predicted = 0.0
    for step in range(forecast_steps):
        point = max(0.0, (slope * (start_index + step)) + intercept)
        predicted += point

    interval_scale = math.sqrt(forecast_steps)
    lower_bound = max(0.0, predicted - (1.28 * std_dev * interval_scale))
    upper_bound = predicted + (1.28 * std_dev * interval_scale)
    return {
        "forecast_date": date.today().isoformat(),
        "horizon_days": horizon_days,
        "predicted_lpg_demand": round(predicted, 2),
        "lower_bound": round(lower_bound, 2),
        "upper_bound": round(upper_bound, 2),
        "model_version": "linear-trend-v1",
    }
