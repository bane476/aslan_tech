def calculate_supply_gap_score(demand_forecast: float, supply_forecast: float) -> float:
    if demand_forecast <= 0:
        return 0.0
    supply_gap_ratio = max(0.0, demand_forecast - supply_forecast) / demand_forecast
    return min(100.0, round(supply_gap_ratio * 100, 2))


def calculate_risk_score(supply_gap_score: float, disruption_score: float) -> float:
    return round((0.60 * supply_gap_score) + (0.40 * disruption_score), 2)


def risk_level_for_score(risk_score: float) -> str:
    if risk_score >= 60:
        return "HIGH"
    if risk_score >= 30:
        return "MEDIUM"
    return "LOW"
