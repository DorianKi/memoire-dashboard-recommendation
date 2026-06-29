def recommend_dashboard(
    kpi_count,
    has_time_series,
    has_table,
    has_alerts,
    filter_count,
    info_density,
    color_hierarchy,
    size_hierarchy
):
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

    if has_table:
        recommendation["table_placement"] = "Bottom section"
    else:
        recommendation["table_placement"] = "Not applicable"

    if filter_count >= 3:
        recommendation["filter_placement"] = "Top row"
    elif filter_count > 0:
        recommendation["filter_placement"] = "Top or side panel"
    else:
        recommendation["filter_placement"] = "No filters"

    if has_alerts:
        recommendation["alerts_placement"] = "Top-right area"
    else:
        recommendation["alerts_placement"] = "Not applicable"

    if info_density == "High" and (color_hierarchy == "Low" or size_hierarchy == "Low"):
        recommendation["overload_risk"] = "High"
        recommendation["expected_affordance_level"] = "Low to moderate"
    elif info_density == "Moderate":
        recommendation["overload_risk"] = "Moderate"
        recommendation["expected_affordance_level"] = "Moderate"
    else:
        recommendation["overload_risk"] = "Low"
        recommendation["expected_affordance_level"] = "Moderate to high"

    return recommendation
    