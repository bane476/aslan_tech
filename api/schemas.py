from datetime import datetime
from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    app: str
    environment: str


class SchedulerStatusResponse(BaseModel):
    enabled: bool
    started: bool
    interval_seconds: int
    horizons: list[int]
    last_run_started_at: str | None = None
    last_run_finished_at: str | None = None
    last_status: str
    last_error: str | None = None
    run_count: int


class DemandForecastResponse(BaseModel):
    as_of: datetime
    data_version: str
    model_version: str
    forecast_date: str
    horizon_days: int
    predicted_lpg_demand: float
    lower_bound: float
    upper_bound: float


class SupplyForecastResponse(BaseModel):
    as_of: datetime
    data_version: str
    model_version: str
    forecast_date: str
    horizon_days: int
    expected_crude_arrival_volume: float
    confidence_band: str


class RiskScoreResponse(BaseModel):
    as_of: datetime
    data_version: str
    horizon_days: int
    supply_gap_score: float
    disruption_score: float
    risk_score: float
    risk_level: str
    top_risk_drivers: list[str]


class AlertItem(BaseModel):
    level: str
    title: str
    message: str
    drivers: list[str]


class AlertsResponse(BaseModel):
    as_of: datetime
    data_version: str
    alerts: list[AlertItem]


class DemandForecastHistoryItem(BaseModel):
    forecast_date: str
    horizon_days: int
    predicted_lpg_demand: float
    lower_bound: float
    upper_bound: float
    model_version: str


class SupplyForecastHistoryItem(BaseModel):
    forecast_date: str
    horizon_days: int
    expected_crude_arrival_volume: float
    confidence_band: str
    model_version: str


class RiskHistoryItem(BaseModel):
    as_of: datetime
    horizon_days: int
    supply_gap_score: float
    disruption_score: float
    risk_score: float
    risk_level: str
    top_risk_drivers: list[str]


class AlertHistoryItem(BaseModel):
    as_of: datetime
    level: str
    title: str
    message: str
    drivers: list[str]


class SourceObservationItem(BaseModel):
    id: int
    source_name: str
    metric_name: str
    observation_date: str
    value: float
    unit: str | None = None


class SourceObservationDetailResponse(BaseModel):
    id: int
    source_name: str
    metric_name: str
    observation_date: str
    value: float
    unit: str | None = None
    source_record: dict[str, Any] | list[Any] | str | None = None


class DemandForecastHistoryResponse(BaseModel):
    data_version: str
    items: list[DemandForecastHistoryItem]


class SupplyForecastHistoryResponse(BaseModel):
    data_version: str
    items: list[SupplyForecastHistoryItem]


class RiskHistoryResponse(BaseModel):
    data_version: str
    items: list[RiskHistoryItem]


class AlertHistoryResponse(BaseModel):
    data_version: str
    items: list[AlertHistoryItem]


class SourceObservationResponse(BaseModel):
    data_version: str
    items: list[SourceObservationItem]


class ScenariosResponse(BaseModel):
    as_of: datetime
    data_version: str
    scenarios: list[dict]


class IngestionResponse(BaseModel):
    source_name: str
    dataset_name: str
    status: str
    loaded_at: datetime
    row_count: int
    null_count: int
    notes: str | None = None
