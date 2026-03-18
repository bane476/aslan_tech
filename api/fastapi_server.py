from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from api.dashboard_page import render_dashboard_html
from api.schemas import (
    AlertHistoryResponse,
    AlertsResponse,
    DemandForecastHistoryResponse,
    DemandForecastResponse,
    HealthResponse,
    IngestionResponse,
    RiskHistoryResponse,
    RiskScoreResponse,
    ScenariosResponse,
    SourceObservationResponse,
    SupplyForecastHistoryResponse,
    SupplyForecastResponse,
)
from app.bootstrap import init_db
from app.config import settings
from app.data_access import (
    latest_data_timestamp,
    load_latest_domestic_observations,
    load_latest_market_observations,
    load_recent_alerts,
    load_recent_demand_forecasts,
    load_recent_risk_snapshots,
    load_recent_supply_forecasts,
    replace_alerts_for_timestamp,
    store_demand_forecast,
    store_risk_snapshot,
    store_supply_forecast,
)
from app.db import get_db
from ingestion.domestic_energy_ingest import ingest_ppac_data
from ingestion.market_ingest import ingest_market_data
from models.demand_forecast.service import forecast_lpg_demand
from models.disruption_detection.service import compute_disruption_score
from models.supply_forecast.service import forecast_crude_supply
from processing.feature_pipeline import build_feature_snapshot
from risk_engine.alert_rules import build_alerts
from risk_engine.risk_scoring import (
    calculate_risk_score,
    calculate_supply_gap_score,
    risk_level_for_score,
)

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def validate_horizon(horizon: int) -> int:
    if horizon not in {30, 60}:
        raise HTTPException(status_code=400, detail="Only 30 and 60 day horizons are supported.")
    return horizon


def validate_history_limit(limit: int) -> int:
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="History limit must be between 1 and 100.")
    return limit


def combined_data_version(db: Session) -> str:
    return f"PPAC:{latest_data_timestamp(db, 'PPAC')}|EIA:{latest_data_timestamp(db, 'EIA')}"


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


@app.get("/dashboard", include_in_schema=False)
def dashboard() -> object:
    return render_dashboard_html()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        environment=settings.app_env,
    )


@app.post("/ingestion/ppac", response_model=IngestionResponse)
def ingest_ppac(
    financial_year_start: int | None = Query(None, description="Financial year start, for example 2025."),
    db: Session = Depends(get_db),
) -> IngestionResponse:
    result = ingest_ppac_data(db, financial_year_start=financial_year_start)
    return IngestionResponse(**result.__dict__)


@app.post("/ingestion/eia", response_model=IngestionResponse)
def ingest_eia(db: Session = Depends(get_db)) -> IngestionResponse:
    result = ingest_market_data(db)
    return IngestionResponse(**result.__dict__)


@app.get("/demand-forecast", response_model=DemandForecastResponse)
def demand_forecast(
    horizon: int = Query(..., description="Forecast horizon in days"),
    db: Session = Depends(get_db),
) -> DemandForecastResponse:
    horizon = validate_horizon(horizon)
    try:
        result = forecast_lpg_demand(db, horizon)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    store_demand_forecast(db, result)
    db.commit()
    return DemandForecastResponse(
        as_of=datetime.now(timezone.utc),
        data_version=latest_data_timestamp(db, "PPAC"),
        **result,
    )


@app.get("/supply-forecast", response_model=SupplyForecastResponse)
def supply_forecast(
    horizon: int = Query(..., description="Forecast horizon in days"),
    db: Session = Depends(get_db),
) -> SupplyForecastResponse:
    horizon = validate_horizon(horizon)
    try:
        result = forecast_crude_supply(db, horizon)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    store_supply_forecast(db, result)
    db.commit()
    return SupplyForecastResponse(
        as_of=datetime.now(timezone.utc),
        data_version=combined_data_version(db),
        **result,
    )


@app.get("/risk-score", response_model=RiskScoreResponse)
def risk_score(
    horizon: int = Query(30, description="Risk horizon in days"),
    db: Session = Depends(get_db),
) -> RiskScoreResponse:
    horizon = validate_horizon(horizon)
    try:
        as_of, payload = build_live_risk_payload(db, horizon)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

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
    db.commit()
    return RiskScoreResponse(
        as_of=as_of,
        data_version=combined_data_version(db),
        **payload,
    )


@app.get("/alerts", response_model=AlertsResponse)
def alerts(
    horizon: int = Query(30, description="Alert horizon in days"),
    db: Session = Depends(get_db),
) -> AlertsResponse:
    horizon = validate_horizon(horizon)
    try:
        as_of, risk_payload = build_live_risk_payload(db, horizon)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    alert_items = build_alerts(
        risk_score=risk_payload["risk_score"],
        supply_gap_score=risk_payload["supply_gap_score"],
        drivers=risk_payload["top_risk_drivers"],
    )
    replace_alerts_for_timestamp(db, as_of=as_of, alerts=alert_items)
    db.commit()
    return AlertsResponse(
        as_of=as_of,
        data_version=combined_data_version(db),
        alerts=alert_items,
    )


@app.get("/history/demand-forecasts", response_model=DemandForecastHistoryResponse)
def demand_forecast_history(
    limit: int = Query(20, description="Maximum number of history rows to return"),
    horizon: int | None = Query(None, description="Optional forecast horizon filter"),
    db: Session = Depends(get_db),
) -> DemandForecastHistoryResponse:
    limit = validate_history_limit(limit)
    if horizon is not None:
        horizon = validate_horizon(horizon)
    return DemandForecastHistoryResponse(
        data_version=latest_data_timestamp(db, "PPAC"),
        items=load_recent_demand_forecasts(db, limit, horizon),
    )


@app.get("/history/supply-forecasts", response_model=SupplyForecastHistoryResponse)
def supply_forecast_history(
    limit: int = Query(20, description="Maximum number of history rows to return"),
    horizon: int | None = Query(None, description="Optional forecast horizon filter"),
    db: Session = Depends(get_db),
) -> SupplyForecastHistoryResponse:
    limit = validate_history_limit(limit)
    if horizon is not None:
        horizon = validate_horizon(horizon)
    return SupplyForecastHistoryResponse(
        data_version=combined_data_version(db),
        items=load_recent_supply_forecasts(db, limit, horizon),
    )


@app.get("/history/risk-snapshots", response_model=RiskHistoryResponse)
def risk_history(
    limit: int = Query(20, description="Maximum number of history rows to return"),
    horizon: int | None = Query(None, description="Optional risk horizon filter"),
    db: Session = Depends(get_db),
) -> RiskHistoryResponse:
    limit = validate_history_limit(limit)
    if horizon is not None:
        horizon = validate_horizon(horizon)
    return RiskHistoryResponse(
        data_version=combined_data_version(db),
        items=load_recent_risk_snapshots(db, limit, horizon),
    )


@app.get("/history/alerts", response_model=AlertHistoryResponse)
def alert_history(
    limit: int = Query(20, description="Maximum number of history rows to return"),
    db: Session = Depends(get_db),
) -> AlertHistoryResponse:
    limit = validate_history_limit(limit)
    return AlertHistoryResponse(
        data_version=combined_data_version(db),
        items=load_recent_alerts(db, limit),
    )


@app.get("/source/domestic-observations", response_model=SourceObservationResponse)
def domestic_observations(
    limit: int = Query(12, description="Maximum number of source rows to return"),
    db: Session = Depends(get_db),
) -> SourceObservationResponse:
    limit = validate_history_limit(limit)
    return SourceObservationResponse(
        data_version=latest_data_timestamp(db, "PPAC"),
        items=load_latest_domestic_observations(db, limit),
    )


@app.get("/source/market-observations", response_model=SourceObservationResponse)
def market_observations(
    limit: int = Query(12, description="Maximum number of source rows to return"),
    db: Session = Depends(get_db),
) -> SourceObservationResponse:
    limit = validate_history_limit(limit)
    return SourceObservationResponse(
        data_version=latest_data_timestamp(db, "EIA"),
        items=load_latest_market_observations(db, limit),
    )


@app.get("/scenarios", response_model=ScenariosResponse)
def scenarios() -> ScenariosResponse:
    return ScenariosResponse(
        as_of=datetime.now(timezone.utc),
        data_version="placeholder-data-v1",
        scenarios=[
            {
                "name": "Saudi export reduction",
                "parameter": "export_drop_pct",
                "default_value": 20,
            },
            {
                "name": "Hormuz vessel slowdown",
                "parameter": "speed_reduction_pct",
                "default_value": 15,
            },
            {
                "name": "Refinery throughput decline",
                "parameter": "refinery_drop_pct",
                "default_value": 10,
            },
        ],
    )
