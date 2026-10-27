"""Moteur de règles simplifié pour recommander une structure de dashboard."""

LEVELS = ("Low", "Moderate", "High")


def _check_count(name, value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} doit être un entier >= 0 (reçu : {value!r})")
    return value


def _check_bool(name, value):
    if not isinstance(value, bool):
        raise ValueError(f"{name} doit être un booléen (reçu : {value!r})")
    return value


def _check_level(name, value):
    if not isinstance(value, str) or value.strip().capitalize() not in LEVELS:
        raise ValueError(f"{name} doit être parmi {LEVELS} (reçu : {value!r})")
    return value.strip().capitalize()


def _overload_risk(info_density, color_hierarchy, size_hierarchy):
    """Retourne (risque, niveau d'affordance, confiance).

    La confiance est une heuristique fixe liée au nombre de signaux qui
    soutiennent la règle. Elle n'est pas encore issue de l'Apriori.
    """
    weak = [color_hierarchy == "Low", size_hierarchy == "Low"]

    if info_density == "High" and any(weak):
        confidence = 0.90 if all(weak) else 0.75
        return "High", "Low to moderate", confidence
    if info_density == "Moderate":
        return "Moderate", "Moderate", 0.60
    if info_density == "High":
        return "Low", "Moderate to high", 0.55
    return "Low", "Moderate to high", 0.80


def recommend_dashboard(
    kpi_count,
    has_time_series,
    has_table,
    has_alerts,
    filter_count,
    info_density,
    color_hierarchy,
    size_hierarchy,
):
    kpi_count = _check_count("kpi_count", kpi_count)
    filter_count = _check_count("filter_count", filter_count)
    has_time_series = _check_bool("has_time_series", has_time_series)
    has_table = _check_bool("has_table", has_table)
    has_alerts = _check_bool("has_alerts", has_alerts)
    info_density = _check_level("info_density", info_density)
    color_hierarchy = _check_level("color_hierarchy", color_hierarchy)
    size_hierarchy = _check_level("size_hierarchy", size_hierarchy)

    recommendation = {}

    if has_table and has_time_series:
        recommendation["recommended_layout"] = "Hybrid layout"
    elif kpi_count >= 3:
        recommendation["recommended_layout"] = "Top KPI overview layout"
    else:
        recommendation["recommended_layout"] = "Simple analytical layout"

    recommendation["kpi_placement"] = "Top row" if kpi_count > 0 else "No KPI block"

    if has_time_series:
        recommendation["time_series_placement"] = "Central area"
        recommendation["recommended_time_series_visual"] = "Line chart"
    else:
        recommendation["time_series_placement"] = "Not applicable"
        recommendation["recommended_time_series_visual"] = "Not applicable"

    recommendation["table_placement"] = "Bottom section" if has_table else "Not applicable"

    if filter_count >= 3:
        recommendation["filter_placement"] = "Top row"
    elif filter_count > 0:
        recommendation["filter_placement"] = "Top or side panel"
    else:
        recommendation["filter_placement"] = "No filters"

    recommendation["alerts_placement"] = "Top-right area" if has_alerts else "Not applicable"

    risk, affordance, confidence = _overload_risk(
        info_density, color_hierarchy, size_hierarchy
    )
    recommendation["overload_risk"] = risk
    recommendation["expected_affordance_level"] = affordance
    recommendation["overload_risk_confidence"] = confidence

    return recommendation
