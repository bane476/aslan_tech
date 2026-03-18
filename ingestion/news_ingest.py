from datetime import datetime

from ingestion.domestic_energy_ingest import IngestionResult


def ingest_news_data() -> IngestionResult:
    return IngestionResult(
        source_name="GDELT",
        dataset_name="energy_news",
        status="placeholder",
        loaded_at=datetime.utcnow(),
        row_count=0,
        null_count=0,
        notes="News ingestion is not implemented yet.",
    )
