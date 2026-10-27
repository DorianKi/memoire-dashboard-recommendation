import pandas as pd
import pytest

from reco_tool.mining import (
    apriori_itemsets, association_rules, build_rules, build_transactions,
    frequency_rules, load_grid,
)


@pytest.fixture(scope="module")
def grid():
    return load_grid()


def test_grille_anonymisee(grid):
    for colonne in ("Nom_Dashboard", "Nom_Page", "Commentaires"):
        assert colonne not in grid.columns
    assert grid["Dashboard_ID"].str.fullmatch(r"D\d+").all()
    assert grid["Page_ID"].str.fullmatch(r"P\d+").all()
    assert len(grid) == 34


def test_resultats_identiques_au_notebook_du_memoire(grid):
    stats = build_rules(grid)["stats"]
    assert stats == {"pages": 34, "itemsets_frequents": 119, "regles_apriori": 27}


def test_regle_densite_forte_implique_surcharge(grid):
    regles = build_rules(grid)["apriori"]
    cible = [
        r for r in regles
        if r["antecedents"] == frozenset({"Densite_info=Forte"})
        and r["consequents"] == frozenset({"Risques_surcharge=Oui"})
    ]
    assert len(cible) == 1
    assert cible[0]["confidence"] == pytest.approx(1.0)


def test_regle_frequentielle_table_en_bas(grid):
    info = build_rules(grid)["frequentielles"]["Tables_detail_emplacement"]
    regle = info["Series_temporelles_present=Oui"]
    assert regle["valeur"] == "bas"
    assert regle["confiance"] == 83.3


def test_transactions_ignorent_les_valeurs_manquantes():
    df = pd.DataFrame({"Layout_dominant": ["Hybride", pd.NA], "KPI_emplacement": [pd.NA, "NA"]})
    out = build_transactions(df, columns=["Layout_dominant", "KPI_emplacement"])
    assert out == [["Layout_dominant=Hybride"], []]


def test_apriori_sur_exemple_simple():
    transactions = [["a", "b"], ["a", "b"], ["a", "c"], ["b"]]
    freq = apriori_itemsets(transactions, min_support=0.5)
    assert freq[frozenset({"a"})] == 0.75
    assert freq[frozenset({"a", "b"})] == 0.5
    assert frozenset({"c"}) not in freq


def test_regles_d_association_sur_exemple_simple():
    transactions = [["a", "b"]] * 3 + [["b"]]
    regles = association_rules(apriori_itemsets(transactions, 0.5), min_confidence=0.9, min_lift=0.5)
    assert any(r["antecedents"] == {"a"} and r["consequents"] == {"b"} for r in regles)


def test_frequence_conditionnelle_exige_cinq_observations():
    df = pd.DataFrame({
        "Series_temporelles_present": ["Oui"] * 4,
        "Tables_detail_emplacement": ["bas"] * 4,
    })
    for col in ("KPI_synthese_present", "Tables_detail_present", "Alertes_present",
                "Densite_info", "Hierarchie_couleur", "Hierarchie_taille"):
        df[col] = "x"
    regles = frequency_rules(df)
    assert regles["Tables_detail_emplacement"] == {}
