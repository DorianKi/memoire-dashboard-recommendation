import pytest

from reco_tool.recommender import recommander

EMPTY_RULES = {"apriori": [], "frequentielles": {}}


def test_cas_usage_1_dense_avec_table():
    r = recommander(
        kpi_present="Oui", nb_kpi=4, serie_present="Oui", table_present="Oui",
        densite="Forte", hierarchie_couleur="Faible", hierarchie_taille="Faible",
    )
    assert r["Tables_detail_emplacement"]["valeur"] == "bas"
    assert r["Tables_detail_emplacement"]["confiance"] == 83.3
    assert r["Risques_surcharge"] == {"valeur": "Oui", "confiance": 100.0, "source": "apriori", "n": None}
    assert r["Layout_dominant"]["source"] == "fallback"
    assert r["Layout_dominant"]["valeur"] == "Hybride"


def test_cas_usage_2_kpi_seul():
    r = recommander(kpi_present="Oui", nb_kpi=7, densite="Moderee", hierarchie_couleur="Moderee")
    assert r["Layout_dominant"]["valeur"] == "Z_pattern"
    assert r["Layout_dominant"]["source"] == "frequentiel"
    assert r["KPI_emplacement"]["note"] == "Attention lisibilité"


@pytest.mark.parametrize(
    "nb_kpi, valeur, note",
    [
        (1, "ligne_supérieure", "Optimal"),
        (5, "ligne_supérieure", "Optimal"),
        (6, "ligne_supérieure", "Attention lisibilité"),
        (10, "ligne_supérieure", "Attention lisibilité"),
        (11, "disperses", "Risque de surcharge élevé"),
    ],
)
def test_seuils_nombre_de_kpi(nb_kpi, valeur, note):
    r = recommander(kpi_present="Oui", nb_kpi=nb_kpi, rules=EMPTY_RULES)
    assert r["KPI_emplacement"]["valeur"] == valeur
    assert r["KPI_emplacement"]["note"] == note


def test_pas_de_kpi_pas_d_emplacement():
    assert "KPI_emplacement" not in recommander(kpi_present="Non", rules=EMPTY_RULES)


@pytest.mark.parametrize(
    "kpi, serie, table, attendu",
    [
        ("Oui", "Oui", "Oui", "Hybride"),
        ("Non", "Oui", "Oui", "Hybride"),
        ("Oui", "Non", "Non", "Z_pattern"),
        ("Non", "Non", "Oui", "Grille"),
        ("Non", "Oui", "Non", "Vertical"),
        ("Non", "Non", "Non", "Hybride"),
    ],
)
def test_layout_fallback(kpi, serie, table, attendu):
    r = recommander(kpi_present=kpi, serie_present=serie, table_present=table, rules=EMPTY_RULES)
    assert r["Layout_dominant"] == {"valeur": attendu, "confiance": None, "source": "fallback", "n": None}


def test_visuels_recommandes():
    r = recommander(kpi_present="Oui", serie_present="Oui", table_present="Oui", rules=EMPTY_RULES)
    assert r["Visuels_recommandes"]["valeur"] == "KPI_card, line_chart / area_chart, table / matrix"
    vide = recommander(rules=EMPTY_RULES)
    assert vide["Visuels_recommandes"]["valeur"].startswith("à définir")


def test_pas_de_regle_apriori_pas_de_risque_invente():
    assert "Risques_surcharge" not in recommander(rules=EMPTY_RULES)


def test_accents_et_casse_acceptes():
    a = recommander(kpi_present="oui", nb_kpi=3, densite="Modérée", hierarchie_couleur="FAIBLE")
    b = recommander(kpi_present="Oui", nb_kpi=3, densite="Moderee", hierarchie_couleur="Faible")
    assert a == b


@pytest.mark.parametrize(
    "overrides",
    [
        {"kpi_present": "peut-être"},
        {"densite": "Extreme"},
        {"hierarchie_taille": None},
        {"nb_kpi": -1},
        {"nb_kpi": True},
        {"nb_filtres": 2.5},
    ],
)
def test_entrees_invalides(overrides):
    with pytest.raises(ValueError):
        recommander(rules=EMPTY_RULES, **overrides)
