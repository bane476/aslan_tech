import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import default_financial_year_start, settings
from app.data_access import log_data_load, replace_domestic_observations
from app.models import DomesticEnergyObservation
from ingestion.common import parse_number, post_json, strip_tags

MONTH_FIELDS = [
    ("april", "April", 4),
    ("may", "May", 5),
    ("june", "June", 6),
    ("july", "July", 7),
    ("august", "August", 8),
    ("september", "September", 9),
    ("october", "October", 10),
    ("november", "November", 11),
    ("december", "December", 12),
    ("january", "January", 1),
    ("february", "February", 2),
    ("march", "March", 3),
]
PPAC_PRODUCTS_DATA_URL = "https://ppac.gov.in/AjaxController/getConsumptionPetroleumProductsData"
PPAC_IMPORT_EXPORT_DATA_URL = "https://ppac.gov.in/AjaxController/getImportExports"
PPAC_PRODUCTS_PAGE_ID = "43"
PPAC_IMPORT_EXPORT_PAGE_ID = "14"
PPAC_REPORT_BY = "1"


@dataclass
class IngestionResult:
    source_name: str
    dataset_name: str
    status: str
    loaded_at: datetime
    row_count: int
    null_count: int
    notes: str | None = None


def _financial_month_to_date(financial_year_start: int, month_number: int) -> date:
    year = financial_year_start if month_number >= 4 else financial_year_start + 1
    return date(year, month_number, 1)


def _financial_year_label(financial_year_start: int) -> str:
    return f"{financial_year_start}-{financial_year_start + 1}"


def _build_monthly_rows(
    metric_name: str,
    record: dict,
    financial_year_start: int,
    unit: str,
) -> list[DomesticEnergyObservation]:
    observations: list[DomesticEnergyObservation] = []
    clean_title = strip_tags(str(record.get("title", "")))
    for field_name, month_label, month_number in MONTH_FIELDS:
        value = parse_number(str(record.get(field_name, "")))
        if value is None:
            continue
        observation_date = _financial_month_to_date(financial_year_start, month_number)
        observations.append(
            DomesticEnergyObservation(
                source_name="PPAC",
                metric_name=metric_name,
                observation_date=observation_date,
                value=value,
                unit=unit,
                region="India",
                period_label=month_label,
                source_record=json.dumps(
                    {
                        "title": clean_title,
                        "field": field_name,
                        "modified_date": record.get("modified_date"),
                    }
                ),
            )
        )
    return observations


def _load_manual_csv() -> list[DomesticEnergyObservation]:
    path = Path(settings.ppac_manual_csv_path)
    if not path.exists():
        return []

    observations: list[DomesticEnergyObservation] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for record in reader:
            observation_date = date.fromisoformat(record["date"])
            region = record.get("state", "India") or "India"
            for metric_name in ("lpg_consumption", "refinery_throughput", "crude_import_volume"):
                raw_value = (record.get(metric_name) or "").strip()
                if not raw_value:
                    continue
                value = parse_number(raw_value)
                if value is None:
                    continue
                observations.append(
                    DomesticEnergyObservation(
                        source_name="PPAC",
                        metric_name=metric_name,
                        observation_date=observation_date,
                        value=value,
                        unit=record.get(f"{metric_name}_unit", "TMT"),
                        region=region,
                        period_label=observation_date.strftime("%B"),
                        source_record=json.dumps(record),
                    )
                )
    return observations


def _find_record(records: list[dict], title: str) -> dict:
    for record in records:
        record_title = strip_tags(str(record.get("title", ""))).strip().lower()
        if record_title == title.lower():
            return record
    raise ValueError(f"Could not find PPAC record for '{title}'.")


def _load_ppac_ajax(financial_year_start: int) -> list[DomesticEnergyObservation]:
    financial_year = _financial_year_label(financial_year_start)
    products_payload = post_json(
        PPAC_PRODUCTS_DATA_URL,
        {"financialYear": financial_year, "reportBy": PPAC_REPORT_BY, "pageId": PPAC_PRODUCTS_PAGE_ID},
    )
    import_export_payload = post_json(
        PPAC_IMPORT_EXPORT_DATA_URL,
        {"financialYear": financial_year, "reportBy": PPAC_REPORT_BY, "pageId": PPAC_IMPORT_EXPORT_PAGE_ID},
    )

    product_records = list((products_payload.get("result") or {}).values())
    import_export_records = list((import_export_payload.get("result") or {}).values())

    lpg_record = _find_record(product_records, "LPG")
    crude_import_record = _find_record(import_export_records, "CRUDE OIL")
    imported_lpg_record = _find_record(import_export_records, "LPG")

    observations = []
    observations.extend(_build_monthly_rows("lpg_consumption", lpg_record, financial_year_start, "TMT"))
    observations.extend(
        _build_monthly_rows("crude_import_volume", crude_import_record, financial_year_start, "TMT")
    )
    observations.extend(
        _build_monthly_rows("imported_lpg_volume", imported_lpg_record, financial_year_start, "TMT")
    )
    return observations


def ingest_ppac_data(
    db: Session,
    *,
    financial_year_start: int | None = None,
    allow_live_scrape: bool = True,
) -> IngestionResult:
    fy_start = financial_year_start or default_financial_year_start()
    observations = _load_manual_csv()
    notes: list[str] = []

    if observations:
        notes.append(f"Loaded manual PPAC CSV from {settings.ppac_manual_csv_path}.")
    elif allow_live_scrape:
        observations = _load_ppac_ajax(fy_start)
        notes.append(f"Loaded PPAC AJAX datasets for FY {fy_start}-{str(fy_start + 1)[-2:]}.")

    if not observations:
        result = IngestionResult(
            source_name="PPAC",
            dataset_name="domestic_energy",
            status="no_data",
            loaded_at=datetime.utcnow(),
            row_count=0,
            null_count=0,
            notes="No PPAC manual CSV found and no live observations were stored.",
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

    row_count = 0
    for metric_name in sorted({item.metric_name for item in observations}):
        metric_rows = [item for item in observations if item.metric_name == metric_name]
        row_count += replace_domestic_observations(db, "PPAC", metric_name, metric_rows)

    result = IngestionResult(
        source_name="PPAC",
        dataset_name="domestic_energy",
        status="success",
        loaded_at=datetime.utcnow(),
        row_count=row_count,
        null_count=0,
        notes=" ".join(notes),
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
