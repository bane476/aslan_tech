import json
from datetime import date, datetime
from typing import Iterable

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import Alert, DataLoad, DemandForecast, DomesticEnergyObservation, MarketObservation, RiskSnapshot, SupplyForecast


def _parse_source_record(raw: str | None):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def replace_domestic_observations(
    db: Session,
    source_name: str,
    metric_name: str,
    rows: Iterable[DomesticEnergyObservation],
) -> int:
    row_list = list(rows)
    if row_list:
        dates = [row.observation_date for row in row_list]
        db.execute(
            delete(DomesticEnergyObservation).where(
                DomesticEnergyObservation.source_name == source_name,
                DomesticEnergyObservation.metric_name == metric_name,
                DomesticEnergyObservation.observation_date.in_(dates),
            )
        )
        db.add_all(row_list)
    return len(row_list)


def replace_market_observations(
    db: Session,
    source_name: str,
    metric_name: str,
    rows: Iterable[MarketObservation],
) -> int:
    row_list = list(rows)
    if row_list:
        dates = [row.observation_date for row in row_list]
        db.execute(
            delete(MarketObservation).where(
                MarketObservation.source_name == source_name,
                MarketObservation.metric_name == metric_name,
                MarketObservation.observation_date.in_(dates),
            )
        )
        db.add_all(row_list)
    return len(row_list)


def log_data_load(
    db: Session,
    *,
    source_name: str,
    dataset_name: str,
    status: str,
    row_count: int,
    null_count: int,
    notes: str | None = None,
) -> DataLoad:
    record = DataLoad(
        source_name=source_name,
        dataset_name=dataset_name,
        status=status,
        loaded_at=datetime.utcnow(),
        row_count=row_count,
        null_count=null_count,
        notes=notes,
    )
    db.add(record)
    return record


def latest_data_timestamp(db: Session, source_name: str) -> str:
    stmt = select(func.max(DataLoad.loaded_at)).where(DataLoad.source_name == source_name)
    latest = db.scalar(stmt)
    return latest.isoformat() if latest else "not-loaded"


def load_domestic_metric_series(db: Session, metric_name: str) -> list[tuple[date, float]]:
    stmt = (
        select(DomesticEnergyObservation.observation_date, DomesticEnergyObservation.value)
        .where(
            DomesticEnergyObservation.metric_name == metric_name,
            DomesticEnergyObservation.region == "India",
        )
        .order_by(DomesticEnergyObservation.observation_date.asc())
    )
    return [(row[0], row[1]) for row in db.execute(stmt).all()]


def load_market_metric_series(db: Session, metric_name: str) -> list[tuple[date, float]]:
    stmt = (
        select(MarketObservation.observation_date, MarketObservation.value)
        .where(MarketObservation.metric_name == metric_name)
        .order_by(MarketObservation.observation_date.asc())
    )
    return [(row[0], row[1]) for row in db.execute(stmt).all()]


def store_demand_forecast(db: Session, payload: dict) -> None:
    forecast_date = date.fromisoformat(payload["forecast_date"])
    db.execute(
        delete(DemandForecast).where(
            DemandForecast.forecast_date == forecast_date,
            DemandForecast.horizon_days == payload["horizon_days"],
            DemandForecast.model_version == payload["model_version"],
        )
    )
    db.add(
        DemandForecast(
            forecast_date=forecast_date,
            horizon_days=payload["horizon_days"],
            predicted_lpg_demand=payload["predicted_lpg_demand"],
            lower_bound=payload["lower_bound"],
            upper_bound=payload["upper_bound"],
            model_version=payload["model_version"],
        )
    )


def store_supply_forecast(db: Session, payload: dict) -> None:
    forecast_date = date.fromisoformat(payload["forecast_date"])
    db.execute(
        delete(SupplyForecast).where(
            SupplyForecast.forecast_date == forecast_date,
            SupplyForecast.horizon_days == payload["horizon_days"],
            SupplyForecast.model_version == payload["model_version"],
        )
    )
    db.add(
        SupplyForecast(
            forecast_date=forecast_date,
            horizon_days=payload["horizon_days"],
            expected_crude_arrival_volume=payload["expected_crude_arrival_volume"],
            confidence_band=payload["confidence_band"],
            model_version=payload["model_version"],
        )
    )


def store_risk_snapshot(
    db: Session,
    *,
    as_of: datetime,
    horizon_days: int,
    supply_gap_score: float,
    disruption_score: float,
    risk_score: float,
    risk_level: str,
    top_risk_drivers: list[str],
) -> None:
    db.add(
        RiskSnapshot(
            as_of=as_of.replace(tzinfo=None),
            horizon_days=horizon_days,
            supply_gap_score=supply_gap_score,
            disruption_score=disruption_score,
            risk_score=risk_score,
            risk_level=risk_level,
            top_risk_drivers=json.dumps(top_risk_drivers),
        )
    )


def replace_alerts_for_timestamp(db: Session, *, as_of: datetime, alerts: list[dict]) -> None:
    naive_as_of = as_of.replace(tzinfo=None)
    db.execute(delete(Alert).where(Alert.as_of == naive_as_of))
    for item in alerts:
        db.add(
            Alert(
                as_of=naive_as_of,
                level=item["level"],
                title=item["title"],
                message=item["message"],
                drivers=json.dumps(item.get("drivers", [])),
            )
        )


def load_recent_demand_forecasts(db: Session, limit: int, horizon_days: int | None = None) -> list[dict]:
    stmt = select(DemandForecast).order_by(DemandForecast.forecast_date.desc(), DemandForecast.id.desc()).limit(limit)
    if horizon_days is not None:
        stmt = stmt.where(DemandForecast.horizon_days == horizon_days)
    rows = db.scalars(stmt).all()
    return [
        {
            "forecast_date": row.forecast_date.isoformat(),
            "horizon_days": row.horizon_days,
            "predicted_lpg_demand": row.predicted_lpg_demand,
            "lower_bound": row.lower_bound,
            "upper_bound": row.upper_bound,
            "model_version": row.model_version,
        }
        for row in rows
    ]


def load_recent_supply_forecasts(db: Session, limit: int, horizon_days: int | None = None) -> list[dict]:
    stmt = select(SupplyForecast).order_by(SupplyForecast.forecast_date.desc(), SupplyForecast.id.desc()).limit(limit)
    if horizon_days is not None:
        stmt = stmt.where(SupplyForecast.horizon_days == horizon_days)
    rows = db.scalars(stmt).all()
    return [
        {
            "forecast_date": row.forecast_date.isoformat(),
            "horizon_days": row.horizon_days,
            "expected_crude_arrival_volume": row.expected_crude_arrival_volume,
            "confidence_band": row.confidence_band,
            "model_version": row.model_version,
        }
        for row in rows
    ]


def load_recent_risk_snapshots(db: Session, limit: int, horizon_days: int | None = None) -> list[dict]:
    stmt = select(RiskSnapshot).order_by(RiskSnapshot.as_of.desc(), RiskSnapshot.id.desc()).limit(limit)
    if horizon_days is not None:
        stmt = stmt.where(RiskSnapshot.horizon_days == horizon_days)
    rows = db.scalars(stmt).all()
    return [
        {
            "as_of": row.as_of,
            "horizon_days": row.horizon_days,
            "supply_gap_score": row.supply_gap_score,
            "disruption_score": row.disruption_score,
            "risk_score": row.risk_score,
            "risk_level": row.risk_level,
            "top_risk_drivers": json.loads(row.top_risk_drivers or "[]"),
        }
        for row in rows
    ]


def load_recent_alerts(db: Session, limit: int) -> list[dict]:
    rows = db.scalars(select(Alert).order_by(Alert.as_of.desc(), Alert.id.desc()).limit(limit)).all()
    return [
        {
            "as_of": row.as_of,
            "level": row.level,
            "title": row.title,
            "message": row.message,
            "drivers": json.loads(row.drivers or "[]"),
        }
        for row in rows
    ]


def load_latest_domestic_observations(db: Session, limit: int) -> list[dict]:
    rows = db.scalars(
        select(DomesticEnergyObservation)
        .where(DomesticEnergyObservation.region == "India")
        .order_by(DomesticEnergyObservation.observation_date.desc(), DomesticEnergyObservation.id.desc())
        .limit(limit)
    ).all()
    return [
        {
            "id": row.id,
            "source_name": row.source_name,
            "metric_name": row.metric_name,
            "observation_date": row.observation_date.isoformat(),
            "value": row.value,
            "unit": row.unit,
        }
        for row in rows
    ]


def load_latest_market_observations(db: Session, limit: int) -> list[dict]:
    rows = db.scalars(
        select(MarketObservation)
        .order_by(MarketObservation.observation_date.desc(), MarketObservation.id.desc())
        .limit(limit)
    ).all()
    return [
        {
            "id": row.id,
            "source_name": row.source_name,
            "metric_name": row.metric_name,
            "observation_date": row.observation_date.isoformat(),
            "value": row.value,
            "unit": row.unit,
        }
        for row in rows
    ]


def load_domestic_observation_detail(db: Session, observation_id: int) -> dict | None:
    row = db.get(DomesticEnergyObservation, observation_id)
    if row is None:
        return None
    return {
        "id": row.id,
        "source_name": row.source_name,
        "metric_name": row.metric_name,
        "observation_date": row.observation_date.isoformat(),
        "value": row.value,
        "unit": row.unit,
        "source_record": _parse_source_record(row.source_record),
    }


def load_market_observation_detail(db: Session, observation_id: int) -> dict | None:
    row = db.get(MarketObservation, observation_id)
    if row is None:
        return None
    return {
        "id": row.id,
        "source_name": row.source_name,
        "metric_name": row.metric_name,
        "observation_date": row.observation_date.isoformat(),
        "value": row.value,
        "unit": row.unit,
        "source_record": _parse_source_record(row.source_record),
    }
