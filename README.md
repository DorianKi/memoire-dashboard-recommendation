# Interactive Dashboard Design Recommendation Tool

This repository presents the research and prototype developed as part of a Master's thesis on interactive dashboard design and strategic decision-making.

The project analyzes recurring dashboard design patterns from real-world Power BI dashboards and translates them into an automated recommendation tool built in Python.

## Overview

Interactive dashboards are not only reporting interfaces; they also shape how decision-makers perceive, interpret, and act on data.

This project explores how dashboard structuring practices can be studied empirically and then formalized into design recommendations. Based on a coded corpus of dashboard pages, the work identifies recurring layout and visualization patterns, extracts robust rules, and integrates them into a prototype recommendation system.

## Objectives

The project was designed around three main objectives:

- Analyze the structure of real-world interactive dashboards used in a business context.
- Identify recurring design patterns related to layout, KPI placement, filters, hierarchy, and information density.
- Transform those patterns into an automated recommendation logic for dashboard design.

## Methodology

The methodology combines empirical analysis and prototype development.

### 1. Dashboard corpus analysis

A corpus of internal Power BI dashboards (13 dashboards) was analyzed through a manually constructed coding grid made of 29 variables. The anonymized grid shared in this repository contains 34 coded pages. The analysis focused on structural and visual dimensions such as:

- dominant layout
- KPI placement
- filter placement
- information density
- visual hierarchy
- chart types
- perceived affordances
- overload risk

### 2. Rule extraction

The coded observations are formalized into recommendation logic at three levels:

1. **Association rules (Apriori)**: minimum support 0.40, minimum confidence 0.90, lift above 1. On the shared grid this gives 119 frequent itemsets and 27 useful rules, mainly predicting the overload risk.
2. **Conditional frequency analysis**: for placements (layout, KPI, series, table, filters) and interaction types, the dominant value for a given context, with at least 5 observations and 60 % frequency.
3. **Fallback logic**: a simple rule based on the elements present when no rule covers the submitted configuration.

### 3. Prototype development

A prototype recommendation tool was developed in Python with an interactive `ipywidgets` interface (`notebooks/02_interactive_tool.ipynb`). Based on user-defined dashboard characteristics, the tool recommends structural choices and highlights potential overload risks. A second notebook (`notebooks/01_demo_recommendation_tool.ipynb`) runs the same engine on three scenarios without the interface.

## Recommendation tool

The prototype takes dashboard design inputs such as:

- presence and number of KPIs
- presence of time series
- presence of detail tables
- presence of alerts
- number of filters (displayed in the interface, not used by the rules yet)
- information density
- color hierarchy level
- size hierarchy level

It then returns recommendations including:

- suggested layout
- KPI placement
- time series, table and filter placement
- interaction types
- dominant visual type and recommended visuals
- expected affordance level
- overload risk

Each rule-based recommendation comes with a confidence percentage computed from the grid and with its source (Apriori, conditional frequency, grid threshold or fallback).

### Use from Python

From the repository root, with `src` on the Python path:

```python
import sys
sys.path.append("src")

from reco_tool import recommander

reco = recommander(
    kpi_present="Oui", nb_kpi=4, serie_present="Oui", table_present="Oui",
    densite="Forte", hierarchie_couleur="Faible", hierarchie_taille="Faible",
)
print(reco["Risques_surcharge"])
# {'valeur': 'Oui', 'confiance': 100.0, 'source': 'apriori', 'n': None}
```

## Repository structure

```text
memoire-dashboard-recommendation/
├── README.md
├── pytest.ini
├── reports/
│   └── MScDM_2026_PEREZ_KIHOUBA_sa.pdf
├── data/
│   └── processed/
│       └── grille_analyse_anonymisee.csv
├── notebooks/
│   ├── 01_demo_recommendation_tool.ipynb
│   └── 02_interactive_tool.ipynb
├── src/
│   └── reco_tool/
│       ├── __init__.py
│       ├── mining.py
│       ├── recommender.py
│       └── ui.py
├── tests/
│   ├── test_mining.py
│   ├── test_recommender.py
│   └── test_ui.py
├── config/
│   └── requirements.txt
└── .gitignore
```

Planned folders (not yet in the repository): `data/raw/`, `figures/` and `src/utils/`.

### Folder description

- `reports/`: public version of the thesis.
- `data/processed/`: anonymized coding grid used to compute the rules.
- `notebooks/`: `01` runs the engine on three scenarios (two thesis use cases and a KPI summary page), `02` is the interactive tool.
- `src/reco_tool/`: `mining.py` extracts the rules, `recommender.py` produces the recommendations, `ui.py` is the `ipywidgets` interface.
- `tests/`: unit tests for the engine and the interface.
- `config/`: project configuration and dependency files.
- `data/raw/` (planned): placeholders or non-shareable source material.
- `src/utils/` (planned): utility functions for loading and preprocessing data.
- `figures/` (planned): images, screenshots, and visuals used in the documentation.

## Tech stack

- Python and pandas
- Jupyter Notebook and ipywidgets
- pytest
- Power BI (source of the analyzed dashboards)
- Association rule mining (Apriori) and conditional frequency analysis

## Setup

Requirements: Python 3.11 or higher.

```bash
git clone git@github.com:DorianKi/memoire-dashboard-recommendation.git
cd memoire-dashboard-recommendation
python -m venv .venv
source .venv/bin/activate
pip install -r config/requirements.txt
jupyter notebook notebooks/02_interactive_tool.ipynb
```

Run the cell, then click the **Obtenir recommandations** button.

## Tests

```bash
pytest -v
```

The tests check that the rule extraction reproduces the thesis figures on the shared grid (34 pages, 119 frequent itemsets, 27 Apriori rules), the recommendations of the two use cases, the KPI thresholds, the fallback logic, input validation and the HTML rendering.

## Data and confidentiality

This repository does not publish confidential internal dashboards from Orange Business.

`data/processed/grille_analyse_anonymisee.csv` contains the coding grid only: one row per page, identified by codes such as D1-P1. Dashboard names, page names and comments have been removed. Values are kept as coded (for example `Moderee` without accent).

Only public, anonymized, transformed, or reproducible materials are intended to be shared here.

## Limitations

- The corpus is small (34 pages from 13 dashboards) and comes from a single organization and tool (Power BI). The rules describe associations observed in this corpus, not causal relationships.
- The coding was done by a single analyst, without inter-coder reliability measure.
- No page of the corpus contains alerts, so the alerts input has no rule of its own.
- The number of filters is displayed but not used by the rules yet.
- The tool is a prototype: its recommendations have not been evaluated experimentally with users.

## Current status

Available in this repository:

- the public version of the thesis
- the anonymized coding grid
- the data-driven recommendation engine (Apriori, conditional frequency, fallback) with confidence per recommendation
- the interactive `ipywidgets` interface
- a demo notebook running the engine on three scenarios
- unit tests (`pytest`)

Still in progress:

- screenshots and visual examples of the prototype
- use of the number of filters in the rules

## Thesis information

- **Program:** MSc Data Management
- **Period:** 2024–2026
- **Author:** Dorian Kihouba
- **Supervisor:** Charles Pérez

## Roadmap

Planned additions to the repository include:

- screenshots and visual examples of the prototype in `figures/`
- rules using the number of filters and the interaction types as inputs
- double coding of the corpus to measure inter-coder agreement
