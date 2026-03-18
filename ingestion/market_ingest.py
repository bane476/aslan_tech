import json
from datetime import date, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.data_access import log_data_load, replace_market_observations
from app.models import MarketObservation
from ingestion.common import fetch_json, load_json_file, parse_number
from ingestion.domestic_energy_ingest import IngestionResult


def _parse_eia_period(period: str) -> date:
    if len(period) == 4:
        return date(int(period), 1, 1)
    if len(period) == 7:
        year, month = period.split("-")
        return date(int(year), int(month), 1)
    return date.fromisoformat(period[:10])


def _load_series_config() -> list[dict]:
    path = Path(settings.eia_series_config_path)
    if not path.exists():
        return []
    loaded = load_json_file(str(path))
    if not isinstance(loaded, list):
        raise ValueError("EIA series config must be a list of series definitions.")
    return loaded


def _build_query_params(config: dict) -> dict:
    params = {
        "api_key": settings.eia_api_key,
        "sort[0][column]": "period",
        "sort[0][direction]": config.get("sort_direction", "desc"),
        "length": config.get("length", 5000),
    }
    if config.get("frequency"):
        params["frequency"] = config["frequency"]
    if config.get("data_fields"):
        params["data[]"] = config["data_fields"]
    if config.get("start"):
        params["start"] = config["start"]
    if config.get("end"):
        params["end"] = config["end"]
    for facet_name, facet_values in config.get("facets", {}).items():
        params[f"facets[{facet_name}][]"] = facet_values
    return params


def ingest_market_data(db: Session) -> IngestionResult:
    configs = _load_series_config()
    if not settings.eia_api_key:
        result = IngestionResult(
            source_name="EIA",
            dataset_name="energy_market",
            status="blocked",
            loaded_at=datetime.utcnow(),
            row_count=0,
            null_count=0,
            notes="EIA_API_KEY is not configured.",
        )
        log_data_load(
            db,
            source_name=result.source_name,
            dataset_name=result.dataset_name,
            status=result.status,
            row_count=result.row_count,
            null_count=result.null_count,
            notes=result.notes,
        )
        db.commit()
        return result

    if not configs:
        result = IngestionResult(
            source_name="EIA",
            dataset_name="energy_market",
            status="blocked",
            loaded_at=datetime.utcnow(),
            row_count=0,
            null_count=0,
            notes=f"No EIA series configuration found at {settings.eia_series_config_path}.",
        )
        log_data_load(
            db,
            source_name=result.source_name,
            dataset_name=result.dataset_name,
            status=result.status,
            row_count=result.row_count,
            null_count=result.null_count,
            notes=result.notes,
        )
        db.commit()
        return result

    stored_rows = 0
    notes: list[str] = []
    for config in configs:
        if "path" in config:
            path = config["path"].lstrip("/")
        elif "series_id" in config:
            path = f"seriesid/{config['series_id']}"
        else:
            raise ValueError("Each EIA series config entry must define either 'path' or 'series_id'.")

        url = f"{settings.eia_base_url.rstrip('/')}/{path}"
        payload = fetch_json(url, params=_build_query_params(config))
        data_rows = payload.get("response", {}).get("data", [])
        observations: list[MarketObservation] = []
        for row in data_rows:
            raw_value = row.get(config.get("value_field", "value"))
            value = parse_number(str(raw_value))
            if value is None:
                continue
            observations.append(
                MarketObservation(
                    source_name="EIA",
                    metric_name=config["metric_name"],
                    observation_date=_parse_eia_period(row["period"]),
                    value=value,
                    unit=row.get(f"{config.get('value_field', 'value')}-units") or config.get("unit"),
                    series_id=config.get("series_id"),
                    source_record=json.dumps(row),
                )
            )
        stored_rows += replace_market_observations(db, "EIA", config["metric_name"], observations)
        notes.append(f"{config['metric_name']}: {len(observations)} rows")

    result = IngestionResult(
        source_name="EIA",
        dataset_name="energy_market",
        status="success",
        loaded_at=datetime.utcnow(),
        row_count=stored_rows,
        null_count=0,
        notes="; ".join(notes),
    )
    log_data_load(
        db,
        source_name=result.source_name,
        dataset_name=result.dataset_name,
        status=result.status,
        row_count=result.row_count,
        null_count=result.null_count,
        notes=result.notes,
    )
    db.commit()
    return result
