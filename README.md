# Global E-Commerce Intelligence Engine

> A big-data analytics platform that transforms raw e-commerce transaction
> data into actionable business intelligence — built for the Elite Tech
> Intern Internship (Data Analytics track).

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Tests](https://img.shields.io/badge/Tests-12%20passing-brightgreen)
![Status](https://img.shields.io/badge/Status-Complete-2DB88A)

## Overview

This project analyzes 51,290 global e-commerce transactions (2012–2015,
23 regions) to surface where the business makes money, where it quietly
loses it, and where revenue is headed next — presented through an
interactive dashboard, not a static report.

## Live demo

**[Open the live dashboard](https://global-ecommerce-intelligence-engine-gta7bwggzhbgqjugpaozt3.streamlit.app)**

## Key findings

- **Tables is the only structurally unprofitable sub-category** (–$64K
  profit overall), driven by average discounts of 38–48% across four
  separate regions — not a one-market anomaly.
- **A hidden risk pocket in Phones (Western Asia)** only surfaces at
  (sub-category × region) granularity — it's invisible in a
  category-level view, since Phones is profitable in aggregate.
- **84 of 390 (sub-category, region) segments — 21.5% — are actively
  losing money**, identified by a rules-based risk engine grounded in
  the EDA rather than arbitrary thresholds.
- **6-month revenue forecast** selected objectively via AIC comparison
  across 4 candidate models, landing on additive-trend /
  multiplicative-seasonal — the only configuration that produced a
  consistent, plausible year-over-year growth pattern (11.7-point
  spread vs. 45+ points for the naive default).

## Features

- [x] Large-scale transaction ingestion and cleaning (Orders, Returns,
      and People sheets merged and validated)
- [x] Profit-risk scoring engine — 390 segments classified into
      Healthy / Watch / High risk tiers
- [x] Revenue forecasting with automated model selection (Holt-Winters,
      AIC-based)
- [x] Interactive Streamlit dashboard with market, category, and year
      filters
- [x] Live currency exchange rate integration (Frankfurter API)
- [x] Automated test suite — 12 tests covering data integrity and
      business-rule regressions

## Tech stack

| Layer | Tools |
|---|---|
| Data processing | Pandas, NumPy, PyArrow |
| Forecasting | statsmodels (Holt-Winters, AIC model selection) |
| Visualization | Plotly |
| Web app | Streamlit |
| Testing | pytest |
| Live data | Frankfurter API (currency rates) |

## Project structure

Global_E-Commerce_Intelligence_Engine/
├── app/
│ ├── main.py # Streamlit entry point
│ ├── theme.py # Design system: colors, fonts, CSS
│ ├── data_loader.py # Cached data loading + live FX fetch
│ └── charts.py # Plotly chart builders
├── data/
│ ├── raw/ # Original Kaggle download (not tracked)
│ └── processed/ # Cleaned data + engine outputs (tracked)
├── notebooks/
│ └── 01_eda.py # Exploratory analysis (# %% cell format)
├── src/
│ ├── clean_data.py
│ ├── diagnose_region_mismatch.py
│ ├── risk_engine.py
│ └── forecast_engine.py
├── tests/
│ └── test_pipeline.py
├── assets/ # README screenshots
├── .streamlit/
│ └── config.toml
├── requirements.txt
└── README.md

## Getting started

```bash
git clone https://github.com/inanbiswas10/Global_E-Commerce_Intelligence_Engine.git
cd Global_E-Commerce_Intelligence_Engine
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app/main.py
```

To rebuild the pipeline from scratch (raw dataset required — see below):

```bash
python src/clean_data.py
python src/risk_engine.py
python src/forecast_engine.py
python -m pytest tests/test_pipeline.py -v
```

## Dataset

[Global Superstore 2016](https://www.kaggle.com/datasets/tahir1413/global-superstore-2016)
(Kaggle) — 51,290 orders across US, Canada, LATAM, Europe, Africa, and
APAC markets. Not included in this repo (see `data/raw/`); download and
place it there to rebuild the pipeline locally.

## Author

Built by Inan Biswas as part of the Elite Tech Intern Internship.