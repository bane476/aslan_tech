from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class DataLoad(Base):
    __tablename__ = "data_loads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_name: Mapped[str] = mapped_column(String(100), index=True)
    dataset_name: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    loaded_at: Mapped[datetime] = mapped_column(DateTime)
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    null_count: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    forecast_date: Mapped[date] = mapped_column(Date, index=True)
    horizon_days: Mapped[int] = mapped_column(Integer, index=True)
    predicted_lpg_demand: Mapped[float] = mapped_column(Float)
    lower_bound: Mapped[float] = mapped_column(Float)
    upper_bound: Mapped[float] = mapped_column(Float)
    model_version: Mapped[str] = mapped_column(String(50), default="baseline-v1")


class SupplyForecast(Base):
    __tablename__ = "supply_forecasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    forecast_date: Mapped[date] = mapped_column(Date, index=True)
    horizon_days: Mapped[int] = mapped_column(Integer, index=True)
    expected_crude_arrival_volume: Mapped[float] = mapped_column(Float)
    confidence_band: Mapped[str] = mapped_column(String(64))
    model_version: Mapped[str] = mapped_column(String(50), default="heuristic-v1")


class RiskSnapshot(Base):
    __tablename__ = "risk_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    as_of: Mapped[datetime] = mapped_column(DateTime, index=True)
    horizon_days: Mapped[int] = mapped_column(Integer, index=True)
    supply_gap_score: Mapped[float] = mapped_column(Float)
    disruption_score: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(16))
    top_risk_drivers: Mapped[str] = mapped_column(Text)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    as_of: Mapped[datetime] = mapped_column(DateTime, index=True)
    level: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    drivers: Mapped[str] = mapped_column(Text)


class DomesticEnergyObservation(Base):
    __tablename__ = "domestic_energy_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_name: Mapped[str] = mapped_column(String(100), index=True)
    metric_name: Mapped[str] = mapped_column(String(100), index=True)
    observation_date: Mapped[date] = mapped_column(Date, index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    region: Mapped[str] = mapped_column(String(100), default="India", index=True)
    period_label: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_record: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MarketObservation(Base):
    __tablename__ = "market_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_name: Mapped[str] = mapped_column(String(100), index=True)
    metric_name: Mapped[str] = mapped_column(String(100), index=True)
    observation_date: Mapped[date] = mapped_column(Date, index=True)
    value: Mapped[float] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(32), nullable=True)
    series_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    source_record: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
