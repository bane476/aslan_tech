from datetime import datetime

from ingestion.domestic_energy_ingest import IngestionResult


def ingest_shipping_data() -> IngestionResult:
    return IngestionResult(
        source_name="shipping",
        dataset_name="vessel_tracking",
        status="placeholder",
        loaded_at=datetime.utcnow(),
        row_count=0,
        null_count=0,
        notes="Shipping ingestion source is not configured yet.",
    )
