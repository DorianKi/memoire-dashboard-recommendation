import pytest

from reco_tool.rules_engine import recommend_dashboard

BASE = dict(
    kpi_count=3,
    has_time_series=False,
    has_table=False,
    has_alerts=False,
    filter_count=0,
    info_density="Low",
    color_hierarchy="Moderate",
    size_hierarchy="Moderate",
)


def reco(**overrides):
    return recommend_dashboard(**{**BASE, **overrides})


# --- Layout ---
def test_hybrid_layout_when_table_and_time_series():
    assert reco(has_table=True, has_time_series=True)["recommended_layout"] == "Hybrid layout"


def test_kpi_overview_layout_from_three_kpis():
    assert reco(kpi_count=3)["recommended_layout"] == "Top KPI overview layout"


def test_simple_layout_with_few_kpis():
    assert reco(kpi_count=2)["recommended_layout"] == "Simple analytical layout"


def test_hybrid_takes_priority_over_kpi_overview():
    r = reco(kpi_count=5, has_table=True, has_time_series=True)
    assert r["recommended_layout"] == "Hybrid layout"


# --- Placements ---
def test_no_kpi_block():
    assert reco(kpi_count=0)["kpi_placement"] == "No KPI block"


def test_time_series_placement():
    r = reco(has_time_series=True)
    assert r["time_series_placement"] == "Central area"
    assert r["recommended_time_series_visual"] == "Line chart"


def test_table_and_alerts_not_applicable_by_default():
    r = reco()
    assert r["table_placement"] == "Not applicable"
    assert r["alerts_placement"] == "Not applicable"


@pytest.mark.parametrize(
    "filters, expected",
    [(0, "No filters"), (1, "Top or side panel"), (2, "Top or side panel"), (3, "Top row")],
)
def test_filter_placement_thresholds(filters, expected):
    assert reco(filter_count=filters)["filter_placement"] == expected


# --- Overload risk ---
def test_high_risk_when_dense_and_both_hierarchies_low():
    r = reco(info_density="High", color_hierarchy="Low", size_hierarchy="Low")
    assert r["overload_risk"] == "High"
    assert r["expected_affordance_level"] == "Low to moderate"
    assert r["overload_risk_confidence"] == 0.90


def test_high_risk_with_one_weak_hierarchy_has_lower_confidence():
    r = reco(info_density="High", color_hierarchy="Low", size_hierarchy="High")
    assert r["overload_risk"] == "High"
    assert r["overload_risk_confidence"] == 0.75


def test_moderate_density_gives_moderate_risk():
    r = reco(info_density="Moderate")
    assert r["overload_risk"] == "Moderate"
    assert r["expected_affordance_level"] == "Moderate"


def test_dense_but_well_structured_is_low_risk():
    r = reco(info_density="High", color_hierarchy="High", size_hierarchy="Moderate")
    assert r["overload_risk"] == "Low"


def test_confidence_is_between_zero_and_one():
    for density in ("Low", "Moderate", "High"):
        assert 0 <= reco(info_density=density)["overload_risk_confidence"] <= 1


# --- Validation ---
def test_levels_are_case_insensitive():
    assert reco(info_density="high", color_hierarchy="low")["overload_risk"] == "High"


@pytest.mark.parametrize(
    "overrides",
    [
        {"kpi_count": -1},
        {"kpi_count": True},
        {"kpi_count": 2.5},
        {"filter_count": "3"},
        {"has_table": "yes"},
        {"has_alerts": 1},
        {"info_density": "Extreme"},
        {"color_hierarchy": None},
    ],
)
def test_invalid_inputs_raise_value_error(overrides):
    with pytest.raises(ValueError):
        reco(**overrides)


# --- Scénarios du notebook ---
def test_notebook_dense_scenario():
    r = recommend_dashboard(5, True, True, True, 5, "High", "Low", "Low")
    assert r["recommended_layout"] == "Hybrid layout"
    assert r["overload_risk"] == "High"
