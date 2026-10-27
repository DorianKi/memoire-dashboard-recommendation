"""Recommandation de structure de dashboard à partir des règles extraites de la grille."""

import unicodedata
from functools import lru_cache

from .mining import build_rules, load_grid

LEVELS = {"faible": "Faible", "moderee": "Moderee", "forte": "Forte"}
YES_NO = {"oui": "Oui", "non": "Non"}


def _strip(text):
    text = unicodedata.normalize("NFKD", str(text))
    return "".join(c for c in text if not unicodedata.combining(c)).strip().lower()


def _check_choice(name, value, mapping):
    key = _strip(value)
    if key not in mapping:
        raise ValueError(f"{name} doit être parmi {sorted(set(mapping.values()))} (reçu : {value!r})")
    return mapping[key]


def _check_count(name, value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} doit être un entier >= 0 (reçu : {value!r})")
    return value


@lru_cache(maxsize=1)
def get_rules():
    """Construit (une seule fois) les règles à partir de la grille anonymisée du dépôt."""
    return build_rules(load_grid())


def _result(valeur, confiance, source, n=None):
    return {"valeur": valeur, "confiance": confiance, "source": source, "n": n}


def recommander(
    kpi_present="Non",
    nb_kpi=0,
    serie_present="Non",
    table_present="Non",
    alerte_present="Non",
    nb_filtres=0,
    densite="Moderee",
    hierarchie_couleur="Faible",
    hierarchie_taille="Faible",
    rules=None,
):
    """Retourne un dictionnaire {cible: {valeur, confiance, source, n}}.

    `confiance` est un pourcentage (float) quand la recommandation vient d'une
    règle de la grille, sinon None. `source` indique l'origine : frequentiel,
    apriori, grille ou fallback.
    """
    kpi_present = _check_choice("kpi_present", kpi_present, YES_NO)
    serie_present = _check_choice("serie_present", serie_present, YES_NO)
    table_present = _check_choice("table_present", table_present, YES_NO)
    alerte_present = _check_choice("alerte_present", alerte_present, YES_NO)
    densite = _check_choice("densite", densite, LEVELS)
    hierarchie_couleur = _check_choice("hierarchie_couleur", hierarchie_couleur, LEVELS)
    hierarchie_taille = _check_choice("hierarchie_taille", hierarchie_taille, LEVELS)
    nb_kpi = _check_count("nb_kpi", nb_kpi)
    nb_filtres = _check_count("nb_filtres", nb_filtres)

    rules = rules or get_rules()
    inputs = {
        "KPI_synthese_present": kpi_present,
        "Series_temporelles_present": serie_present,
        "Tables_detail_present": table_present,
        "Alertes_present": alerte_present,
        "Densite_info": densite,
        "Hierarchie_couleur": hierarchie_couleur,
        "Hierarchie_taille": hierarchie_taille,
    }
    results = {}

    # Niveau 2 : règles fréquentielles, on garde la plus confiante par cible
    for target, target_rules in rules["frequentielles"].items():
        matches = []
        for cond_key, info in target_rules.items():
            cond_col, cond_val = cond_key.split("=", 1)
            if inputs.get(cond_col) == cond_val:
                matches.append((info["confiance"], info["valeur"], info["n"]))
        if matches:
            confiance, valeur, n = max(matches)
            results[target] = _result(valeur, confiance, "frequentiel", n)

    # Niveau 1 : règles Apriori pour le risque de surcharge
    input_items = frozenset(f"{k}={v}" for k, v in inputs.items())
    for rule in rules["apriori"]:
        if not rule["antecedents"] <= input_items:
            continue
        for item in rule["consequents"]:
            if item.startswith("Risques_surcharge"):
                _, valeur = item.split("=", 1)
                confiance = round(rule["confidence"] * 100, 1)
                current = results.get("Risques_surcharge")
                if current is None or confiance > current["confiance"]:
                    results["Risques_surcharge"] = _result(valeur, confiance, "apriori")

    # Nombre de KPI -> emplacement (seuils issus de la grille)
    if kpi_present == "Oui":
        if nb_kpi <= 5:
            emplacement, note = "ligne_supérieure", "Optimal"
        elif nb_kpi <= 10:
            emplacement, note = "ligne_supérieure", "Attention lisibilité"
        else:
            emplacement, note = "disperses", "Risque de surcharge élevé"
        results["KPI_emplacement"] = {
            "valeur": emplacement, "confiance": None,
            "source": "grille", "n": nb_kpi, "note": note,
        }

    # Visuels recommandés selon les éléments présents
    visuels = []
    if kpi_present == "Oui":
        visuels.append("KPI_card")
    if serie_present == "Oui":
        visuels.append("line_chart / area_chart")
    if table_present == "Oui":
        visuels.append("table / matrix")
    results["Visuels_recommandes"] = _result(
        ", ".join(visuels) if visuels else "à définir selon les données", None, "elements"
    )

    # Niveau 3 : fallback pour le layout
    if "Layout_dominant" not in results:
        if serie_present == "Oui" and table_present == "Oui":
            layout = "Hybride"
        elif kpi_present == "Oui" and serie_present == "Non":
            layout = "Z_pattern"
        elif table_present == "Oui" and serie_present == "Non":
            layout = "Grille"
        elif serie_present == "Oui" and kpi_present == "Non":
            layout = "Vertical"
        else:
            layout = "Hybride"
        results["Layout_dominant"] = _result(layout, None, "fallback")

    return results
