# Aslan Technologies Energy Risk Platform

Phase 1 MVP scaffold for an India-focused crude oil and LPG supply risk platform.

## Current Status

This repository now provides:

- FastAPI backend running in Docker
- PostgreSQL running in Docker
- PPAC ingestion into relational storage
- EIA ingestion into relational storage
- baseline LPG demand forecast driven by stored PPAC data
- market-adjusted crude supply and disruption signals driven by EIA data
- persisted demand forecasts, supply forecasts, risk snapshots, and alerts
- history endpoints for persisted model artifacts
- source-observation endpoints for latest PPAC and EIA inputs
- an operator dashboard at `/dashboard` with horizon switching, manual refresh, delta comparisons, history tables, and source-input evidence panels

## What Works Today

- `POST /ingestion/ppac`
  Loads monthly PPAC LPG consumption, crude oil imports, and imported LPG volumes into PostgreSQL.
- `POST /ingestion/eia`
  Loads Brent, WTI, and US commercial crude inventory proxy series into PostgreSQL.
- `GET /demand-forecast?horizon=30|60`
  Returns a baseline LPG demand forecast using stored PPAC monthly history and persists the forecast artifact.
- `GET /supply-forecast?horizon=30|60`
  Returns a market-adjusted crude supply forecast using PPAC imports and EIA market signals and persists the forecast artifact.
- `GET /risk-score?horizon=30|60`
  Returns a risk score using a market-adjusted LPG import supply proxy plus EIA disruption signals and persists the snapshot.
- `GET /alerts?horizon=30|60`
  Returns alert outputs and persists alert records for the run.
- `GET /history/demand-forecasts`
  Returns persisted demand forecast history.
- `GET /history/supply-forecasts`
  Returns persisted supply forecast history.
- `GET /history/risk-snapshots`
  Returns persisted risk snapshot history.
- `GET /history/alerts`
  Returns persisted alert history.
- `GET /source/domestic-observations`
  Returns latest stored PPAC domestic input observations.
- `GET /source/market-observations`
  Returns latest stored EIA market input observations.
- `GET /dashboard`
  Serves an operator dashboard that visualizes persisted history, supports 30/60 day switching, can trigger fresh model runs, compares the latest run to the previous one, and shows the latest PPAC and EIA source inputs.
- `GET /health`
  Basic API health check.

## Local Run

```bash
docker compose up --build -d
```

Health check:

```bash
http://localhost:8000/health
```

Load PPAC data:

```bash
http://localhost:8000/ingestion/ppac
```

Load EIA data:

```bash
http://localhost:8000/ingestion/eia
```

Fetch forecasts and dashboard:

```bash
http://localhost:8000/demand-forecast?horizon=30
http://localhost:8000/supply-forecast?horizon=30
http://localhost:8000/risk-score?horizon=30
http://localhost:8000/alerts?horizon=30
http://localhost:8000/dashboard
```

Fetch history and source evidence:

```bash
http://localhost:8000/history/demand-forecasts?limit=20
http://localhost:8000/history/supply-forecasts?limit=20
http://localhost:8000/history/risk-snapshots?limit=20
http://localhost:8000/history/alerts?limit=20
http://localhost:8000/source/domestic-observations?limit=12
http://localhost:8000/source/market-observations?limit=12
```

## EIA Setup

Add these values to `.env` or your container environment:

- `EIA_API_KEY`
- `EIA_SERIES_CONFIG_PATH`

Then create `data_sources/energy_market/eia_series.json` based on:

- `data_sources/energy_market/eia_series.example.json`

## PPAC Manual Override

If you want to load a manual PPAC CSV instead of the live PPAC feed, place a file at:

- `data_sources/domestic_energy/ppac_monthly_data.csv`

You can use:

- `data_sources/domestic_energy/ppac_monthly_data.template.csv`

## Next Build Steps

1. Add drill-down pages for full source record details behind each observation.
2. Expand PPAC ingestion to refinery throughput and other domestic indicators.
3. Strengthen the demand model beyond a simple linear monthly baseline.
4. Add evaluation and backtesting for forecast quality.
5. Introduce scenario persistence instead of static scenario definitions.
