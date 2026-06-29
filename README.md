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

A corpus of 35 internal Power BI dashboard pages was analyzed through a manually constructed coding grid made of 29 variables. The analysis focused on structural and visual dimensions such as:

- dominant layout
- KPI placement
- filter placement
- information density
- visual hierarchy
- chart types
- perceived affordances
- overload risk

### 2. Rule extraction

The coded observations were formalized into recommendation logic using:

- association rules with the Apriori algorithm
- conditional frequency analysis
- a fallback logic for rare or uncovered configurations

### 3. Prototype development

A prototype recommendation tool was developed in Python and implemented in Jupyter Notebook using `ipywidgets`. Based on user-defined dashboard characteristics, the tool recommends structural choices and highlights potential overload risks.

## Recommendation tool

The prototype takes dashboard design inputs such as:

- number of KPIs
- presence of time series
- presence of detail tables
- presence of alerts
- number of filters
- desired information density
- color hierarchy level
- size hierarchy level

It then returns recommendations including:

- suggested layout
- KPI placement
- filter placement
- table placement
- interaction types
- expected affordance level
- overload risk with confidence score

## Repository structure

```text
memoire-dashboard-recommendation/
├── README.md
├── reports/
│   └── memoire_MScDM_2026_public.pdf
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
│   ├── reco_tool/
│   └── utils/
├── figures/
├── config/
└── .gitignore
```

### Folder description

- `reports/`: public version of the thesis.
- `data/raw/`: placeholders or non-shareable source material.
- `data/processed/`: processed or anonymized data prepared for analysis.
- `notebooks/`: exploratory analysis, rule extraction, and prototype notebooks.
- `src/reco_tool/`: source code for the recommendation engine.
- `src/utils/`: utility functions for loading and preprocessing data.
- `figures/`: images, screenshots, and visuals used in the documentation.
- `config/`: project configuration and dependency files.

## Tech stack

- Python
- Jupyter Notebook
- ipywidgets
- Power BI
- Association rule mining
- Data visualization and dashboard analysis

## Setup

To clone and explore the project locally:

```bash
git clone git@github.com:DorianKi/memoire-dashboard-recommendation.git
cd memoire-dashboard-recommendation
```

If dependency files are added later, install them with one of the following:

```bash
pip install -r config/requirements.txt
```

or

```bash
conda env create -f config/environment.yml
```

## Confidentiality

This repository does not publish confidential internal dashboards from Orange Business.

Only public, anonymized, transformed, or reproducible materials are intended to be shared here. Some elements of the original research corpus cannot be released due to professional confidentiality constraints.

## Current status

This repository is being progressively expanded to include:

- the public version of the thesis
- selected notebooks used for analysis
- a simplified or reproducible version of the recommendation tool
- supporting figures and examples

## Thesis information

- **Program:** MSc Data Management
- **Period:** 2024–2026
- **Author:** Dorian Kihouba
- **Supervisor:** Charles Pérez

## Roadmap

Planned additions to the repository include:

- cleaned and shareable analytical material
- a demonstration notebook for the recommendation tool
- reusable Python modules for recommendation rules
- visual examples and screenshots of the prototype
