"""Extraction des règles : Apriori, analyse fréquentielle conditionnelle.

Reproduit la méthode du mémoire :
- niveau 1 : règles d'association Apriori (support >= 0,40, confiance >= 0,90, lift > 1) ;
- niveau 2 : fréquence conditionnelle (au moins 5 observations et 60 % de fréquence).
"""

from itertools import combinations
from pathlib import Path

import pandas as pd

DEFAULT_GRID = Path(__file__).resolve().parents[2] / "data" / "processed" / "grille_analyse_anonymisee.csv"

TRANSACTION_COLUMNS = [
    "KPI_synthese_present", "KPI_emplacement",
    "Series_temporelles_present", "Series_temporelles_emplacement",
    "Tables_detail_present", "Tables_detail_emplacement",
    "Alertes_present", "Alertes_emplacement",
    "Filtres_emplacement", "Filtres_lisibilite",
    "Interactions_types", "Hierarchie_couleur", "Hierarchie_taille",
    "Densite_info", "Risques_surcharge", "Affordances_actions", "Layout_dominant",
]

APRIORI_TARGETS = (
    "Layout_dominant", "KPI_emplacement", "Series_temporelles_emplacement",
    "Tables_detail_emplacement", "Filtres_emplacement", "Risques_surcharge",
    "Affordances_actions",
)

FREQUENCY_TARGETS = [
    "Layout_dominant", "KPI_emplacement", "Series_temporelles_emplacement",
    "Tables_detail_emplacement", "Filtres_emplacement", "Affordances_actions",
    "Interactions_types", "Types_visuels",
]

FREQUENCY_CONDITIONS = [
    "KPI_synthese_present", "Series_temporelles_present", "Tables_detail_present",
    "Alertes_present", "Densite_info", "Hierarchie_couleur", "Hierarchie_taille",
]

MISSING = {"", "NA", "nan", "NaN"}


def load_grid(path=None):
    """Charge la grille de codage anonymisée (une ligne par page de dashboard)."""
    path = Path(path) if path else DEFAULT_GRID
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    return df.replace({value: pd.NA for value in MISSING})


def build_transactions(df, columns=TRANSACTION_COLUMNS):
    """Convertit chaque page en liste d'items de la forme 'variable=valeur'."""
    transactions = []
    for _, row in df.iterrows():
        items = []
        for col in columns:
            value = row[col]
            if pd.notna(value) and str(value).strip() not in MISSING:
                items.append(f"{col}={str(value).strip()}")
        transactions.append(items)
    return transactions


def apriori_itemsets(transactions, min_support=0.40):
    """Retourne {itemset (frozenset): support} pour les itemsets fréquents."""
    n = len(transactions)
    sets = [frozenset(t) for t in transactions]
    singles = {}
    for t in sets:
        for item in t:
            singles[frozenset([item])] = singles.get(frozenset([item]), 0) + 1
    frequent = {k: v / n for k, v in singles.items() if v / n >= min_support}
    current = list(frequent)
    size = 2
    while current:
        candidates = {a | b for a, b in combinations(current, 2) if len(a | b) == size}
        current = []
        for cand in candidates:
            support = sum(cand <= t for t in sets) / n
            if support >= min_support:
                frequent[cand] = support
                current.append(cand)
        size += 1
    return frequent


def association_rules(frequent, min_confidence=0.90, min_lift=1.0):
    """Génère les règles A -> B avec confiance >= min_confidence et lift > min_lift."""
    rules = []
    for itemset, support in frequent.items():
        if len(itemset) < 2:
            continue
        for r in range(1, len(itemset)):
            for antecedent in combinations(sorted(itemset), r):
                antecedent = frozenset(antecedent)
                consequent = itemset - antecedent
                confidence = support / frequent[antecedent]
                lift = confidence / frequent[consequent]
                if confidence >= min_confidence and lift > min_lift:
                    rules.append({
                        "antecedents": antecedent,
                        "consequents": consequent,
                        "support": support,
                        "confidence": confidence,
                        "lift": lift,
                    })
    rules.sort(key=lambda r: (r["confidence"], r["lift"]), reverse=True)
    return rules


def is_target(consequents, targets=APRIORI_TARGETS):
    return any(item.startswith(tuple(targets)) for item in consequents)


def frequency_rules(df, min_obs=5, min_freq=0.60):
    """Règles fréquentielles : valeur dominante d'une cible sachant une condition."""
    rules = {}
    for target in FREQUENCY_TARGETS:
        if target not in df.columns:
            continue
        rules[target] = {}
        for cond_col in FREQUENCY_CONDITIONS:
            for cond_val in df[cond_col].dropna().unique():
                subset = df.loc[df[cond_col] == cond_val, target].dropna()
                if len(subset) < min_obs:
                    continue
                dominant = subset.mode().iloc[0]
                share = float((subset == dominant).mean())
                if share >= min_freq:
                    rules[target][f"{cond_col}={cond_val}"] = {
                        "valeur": dominant,
                        "confiance": round(share * 100, 1),
                        "n": int(len(subset)),
                    }
    return rules


def build_rules(df=None, min_support=0.40, min_confidence=0.90, min_lift=1.0):
    """Construit toutes les règles à partir de la grille.

    Retourne un dictionnaire avec les règles Apriori utiles, les règles
    fréquentielles et quelques statistiques de contrôle.
    """
    if df is None:
        df = load_grid()
    transactions = build_transactions(df)
    frequent = apriori_itemsets(transactions, min_support)
    rules = association_rules(frequent, min_confidence, min_lift)
    useful = [r for r in rules if is_target(r["consequents"])]
    return {
        "apriori": useful,
        "frequentielles": frequency_rules(df),
        "stats": {
            "pages": len(df),
            "itemsets_frequents": len(frequent),
            "regles_apriori": len(useful),
        },
    }
