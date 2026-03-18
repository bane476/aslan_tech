from datetime import date

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Aslan Energy Risk API"
    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "sqlite:///./aslan_energy.db"
    ppac_products_url: str = "https://ppac.gov.in/consumption/products-wise"
    ppac_import_export_url: str = "https://ppac.gov.in/import-export"
    ppac_manual_csv_path: str = "data_sources/domestic_energy/ppac_monthly_data.csv"
    eia_api_key: str = ""
    eia_base_url: str = "https://api.eia.gov/v2"
    eia_series_config_path: str = "data_sources/energy_market/eia_series.json"
    scheduler_enabled: bool = True
    scheduler_interval_seconds: int = 3600
    scheduler_run_on_startup: bool = True
    scheduler_horizons: str = "30,60"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


def default_financial_year_start(reference_date: date | None = None) -> int:
    current = reference_date or date.today()
    return current.year if current.month >= 4 else current.year - 1


def scheduler_horizon_values() -> list[int]:
    values: list[int] = []
    for item in settings.scheduler_horizons.split(","):
        stripped = item.strip()
        if not stripped:
            continue
        horizon = int(stripped)
        if horizon not in {30, 60}:
            raise ValueError("SCHEDULER_HORIZONS only supports 30 and 60 day horizons.")
        values.append(horizon)
    return values or [30, 60]
