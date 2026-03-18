from sqlalchemy.orm import Session

from processing.feature_pipeline import build_feature_snapshot


def compute_disruption_score(db: Session, horizon_days: int) -> dict:
    snapshot = build_feature_snapshot(db, horizon_days)
    drivers: list[str] = []

    if snapshot.price_pressure >= 0.08:
        drivers.append(
            f"Spot crude prices are running {round(snapshot.price_pressure * 100, 1)}% above the recent baseline."
        )
    if snapshot.inventory_tightness >= 0.03 and snapshot.inventory_latest is not None:
        drivers.append(
            f"US commercial crude inventories are {round(snapshot.inventory_tightness * 100, 1)}% below the recent average."
        )
    if snapshot.price_volatility >= 0.04:
        drivers.append(
            f"Oil market volatility remains elevated at {round(snapshot.price_volatility * 100, 1)}% of mean price."
        )
    if not drivers:
        drivers.append("Market stress indicators are close to baseline.")

    return {
        "horizon_days": horizon_days,
        "disruption_score": snapshot.disruption_signal,
        "signal_version": "market-stress-v1",
        "drivers": drivers,
    }
