from risk_engine.risk_scoring import risk_level_for_score


def build_alerts(risk_score: float, supply_gap_score: float, drivers: list[str]) -> list[dict]:
    alerts: list[dict] = []
    if risk_score >= 60:
        alerts.append(
            {
                "level": risk_level_for_score(risk_score),
                "title": "Energy Supply Alert",
                "message": "Risk score is above the alert threshold.",
                "drivers": drivers,
            }
        )
    elif supply_gap_score >= 40:
        alerts.append(
            {
                "level": "WATCHLIST",
                "title": "Supply Gap Watchlist",
                "message": "Supply gap score is elevated and requires analyst review.",
                "drivers": drivers,
            }
        )
    return alerts
