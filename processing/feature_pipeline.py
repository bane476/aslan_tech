import math
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.data_access import load_domestic_metric_series, load_market_metric_series


@dataclass
class FeatureSnapshot:
    horizon_days: int
    supply_signal: float
    lpg_supply_signal: float
    disruption_signal: float
    price_pressure: float
    inventory_tightness: float
    price_volatility: float
    baseline_crude_volume: float
    baseline_lpg_import_volume: float
    brent_latest: float | None
    wti_latest: float | None
    inventory_latest: float | None


def _clip(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _latest_value(series: list[tuple[object, float]]) -> float | None:
    return series[-1][1] if series else None


def _average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _recent_average(series: list[tuple[object, float]], window: int) -> float:
    values = [value for _, value in series[-window:]]
    return _average(values)


def _relative_change(current: float | None, baseline: float) -> float:
    if current is None or baseline <= 0:
        return 0.0
    return (current - baseline) / baseline


def _coefficient_of_variation(series: list[tuple[object, float]], window: int) -> float:
    values = [value for _, value in series[-window:]]
    if len(values) < 2:
        return 0.0
    mean_value = _average(values)
    if mean_value <= 0:
        return 0.0
    variance = sum((value - mean_value) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance) / mean_value


def build_feature_snapshot(db: Session, horizon_days: int) -> FeatureSnapshot:
    crude_imports = load_domestic_metric_series(db, "crude_import_volume")
    imported_lpg = load_domestic_metric_series(db, "imported_lpg_volume")
    if not crude_imports:
        raise ValueError("No PPAC crude import data is available. Run PPAC ingestion first.")
    if not imported_lpg:
        raise ValueError("No PPAC imported LPG data is available. Run PPAC ingestion first.")

    brent_series = load_market_metric_series(db, "brent_price")
    wti_series = load_market_metric_series(db, "wti_price")
    inventory_series = load_market_metric_series(db, "us_commercial_crude_inventory")

    months = 1 if horizon_days == 30 else 2
    monthly_crude_baseline = _recent_average(crude_imports, 3) or crude_imports[-1][1]
    monthly_lpg_baseline = _recent_average(imported_lpg, 3) or imported_lpg[-1][1]
    baseline_crude_volume = monthly_crude_baseline * months
    baseline_lpg_import_volume = monthly_lpg_baseline * months

    brent_latest = _latest_value(brent_series)
    wti_latest = _latest_value(wti_series)
    inventory_latest = _latest_value(inventory_series)

    brent_change = _relative_change(brent_latest, _recent_average(brent_series, 20))
    wti_change = _relative_change(wti_latest, _recent_average(wti_series, 20))
    positive_price_moves = [change for change in (brent_change, wti_change) if change > 0]
    price_pressure = _clip(_average(positive_price_moves), 0.0, 0.5) if positive_price_moves else 0.0

    inventory_baseline = _recent_average(inventory_series, 12)
    if inventory_latest is not None and inventory_baseline > 0:
        inventory_tightness = _clip((inventory_baseline - inventory_latest) / inventory_baseline, 0.0, 0.35)
    else:
        inventory_tightness = 0.0

    price_volatility = _clip(
        _average(
            [
                _coefficient_of_variation(brent_series, 10),
                _coefficient_of_variation(wti_series, 10),
            ]
        ),
        0.0,
        0.25,
    )

    crude_supply_adjustment = 1.0 - (0.18 * price_pressure) - (0.22 * inventory_tightness) - (0.10 * price_volatility)
    lpg_supply_adjustment = 1.0 - (0.35 * price_pressure) - (0.25 * inventory_tightness) - (0.10 * price_volatility)
    supply_signal = max(0.0, baseline_crude_volume * max(0.7, crude_supply_adjustment))
    lpg_supply_signal = max(0.0, baseline_lpg_import_volume * max(0.65, lpg_supply_adjustment))

    disruption_score = min(
        100.0,
        round(
            (price_pressure * 100 * 0.45)
            + (inventory_tightness * 100 * 0.35)
            + (price_volatility * 100 * 0.20),
            2,
        ),
    )

    return FeatureSnapshot(
        horizon_days=horizon_days,
        supply_signal=round(supply_signal, 2),
        lpg_supply_signal=round(lpg_supply_signal, 2),
        disruption_signal=disruption_score,
        price_pressure=round(price_pressure, 4),
        inventory_tightness=round(inventory_tightness, 4),
        price_volatility=round(price_volatility, 4),
        baseline_crude_volume=round(baseline_crude_volume, 2),
        baseline_lpg_import_volume=round(baseline_lpg_import_volume, 2),
        brent_latest=brent_latest,
        wti_latest=wti_latest,
        inventory_latest=inventory_latest,
    )
