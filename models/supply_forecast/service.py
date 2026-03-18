from datetime import date

from sqlalchemy.orm import Session

from processing.feature_pipeline import build_feature_snapshot


def forecast_crude_supply(db: Session, horizon_days: int) -> dict:
    snapshot = build_feature_snapshot(db, horizon_days)
    prediction = snapshot.supply_signal
    confidence_width = max(500.0, prediction * (0.06 + snapshot.price_volatility + (0.5 * snapshot.inventory_tightness)))
    return {
        "forecast_date": date.today().isoformat(),
        "horizon_days": horizon_days,
        "expected_crude_arrival_volume": prediction,
        "confidence_band": f"{round(max(0.0, prediction - confidence_width), 2)}-{round(prediction + confidence_width, 2)}",
        "model_version": "market-adjusted-v1",
    }
