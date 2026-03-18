from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.data_access import (
    replace_alerts_for_timestamp,
    store_demand_forecast,
    store_risk_snapshot,
    store_supply_forecast,
)
from models.demand_forecast.service import forecast_lpg_demand
from models.disruption_detection.service import compute_disruption_score
from models.supply_forecast.service import forecast_crude_supply
from processing.feature_pipeline import build_feature_snapshot
from risk_engine.alert_rules import build_alerts
from risk_engine.risk_scoring import calculate_risk_score, calculate_supply_gap_score, risk_level_for_score


def build_live_risk_payload(db: Session, horizon: int) -> tuple[datetime, dict]:
    snapshot = build_feature_snapshot(db, horizon)
    demand = forecast_lpg_demand(db, horizon)
    disruption = compute_disruption_score(db, horizon)
    supply_gap_score = calculate_supply_gap_score(
        demand["predicted_lpg_demand"],
        snapshot.lpg_supply_signal,
    )
    risk_score = calculate_risk_score(supply_gap_score, disruption["disruption_score"])
    risk_level = risk_level_for_score(risk_score)
    drivers = [
        f"Market-adjusted LPG import supply proxy is {round(snapshot.lpg_supply_signal, 2)} against demand forecast {demand['predicted_lpg_demand']}",
        *disruption["drivers"],
    ]
    as_of = datetime.now(timezone.utc)
    payload = {
        "horizon_days": horizon,
        "supply_gap_score": supply_gap_score,
        "disruption_score": disruption["disruption_score"],
        "risk_score": risk_score,
        "risk_level": risk_level,
        "top_risk_drivers": drivers,
    }
    return as_of, payload


def materialize_demand_forecast(db: Session, horizon: int) -> dict:
    result = forecast_lpg_demand(db, horizon)
    store_demand_forecast(db, result)
    return result


def materialize_supply_forecast(db: Session, horizon: int) -> dict:
    result = forecast_crude_supply(db, horizon)
    store_supply_forecast(db, result)
    return result


def materialize_risk_snapshot(db: Session, horizon: int) -> tuple[datetime, dict]:
    as_of, payload = build_live_risk_payload(db, horizon)
    store_risk_snapshot(
        db,
        as_of=as_of,
        horizon_days=payload["horizon_days"],
        supply_gap_score=payload["supply_gap_score"],
        disruption_score=payload["disruption_score"],
        risk_score=payload["risk_score"],
        risk_level=payload["risk_level"],
        top_risk_drivers=payload["top_risk_drivers"],
    )
    return as_of, payload


def materialize_alerts(db: Session, horizon: int) -> tuple[datetime, list[dict]]:
    as_of, risk_payload = build_live_risk_payload(db, horizon)
    alert_items = build_alerts(
        risk_score=risk_payload["risk_score"],
        supply_gap_score=risk_payload["supply_gap_score"],
        drivers=risk_payload["top_risk_drivers"],
    )
    replace_alerts_for_timestamp(db, as_of=as_of, alerts=alert_items)
    return as_of, alert_items


def materialize_full_run(db: Session, horizons: list[int]) -> dict:
    run_summary: dict[str, dict] = {}
    for horizon in horizons:
        demand = materialize_demand_forecast(db, horizon)
        supply = materialize_supply_forecast(db, horizon)
        risk_as_of, risk_payload = materialize_risk_snapshot(db, horizon)
        alerts_as_of, alerts = materialize_alerts(db, horizon)
        run_summary[str(horizon)] = {
            "demand_forecast": demand,
            "supply_forecast": supply,
            "risk_snapshot": {"as_of": risk_as_of.isoformat(), **risk_payload},
            "alerts": {"as_of": alerts_as_of.isoformat(), "items": alerts},
        }
    db.commit()
    return run_summary
