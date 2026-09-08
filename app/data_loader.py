# app/data_loader.py

# Loads the processed datasets produced by the Day 2/3 scripts, and fetches
# a live currency exchange rate from the free Frankfurter API. All functions
# use Streamlit's caching so the dashboard stays fast on every rerun - the
# parquet files reload only when needed, and the live FX rate refreshes on
# its own schedule rather than on every single user interaction.

import pandas as pd
import requests
import streamlit as st

ORDERS_PATH = "data/processed/orders_clean.parquet"
RISK_PATH = "data/processed/risk_scores.parquet"
FORECAST_PATH = "data/processed/revenue_forecast.parquet"

FX_API_URL = "https://api.frankfurter.dev/v1/latest"

@st.cache_data
def load_orders ():

    # Loads the cleaned, joined orders dataset from Day 2.

    return pd.read_parquet (ORDERS_PATH)

@st.cache_data
def load_risk_scores ():

    # Loads the (sub_category, region) risk scores from Day 3.

    return pd.read_parquet (RISK_PATH)

@st.cache_data
def load_forecast ():

    # Loads the actual + forecast monthly revenue series from Day 3.

    return pd.read_parquet (FORECAST_PATH)

@st.cache_data (ttl = 3600)  # refresh once per hour - rates don't move faster than that
def fetch_live_fx_rate (base = "USD",target = "EUR"):

    # Fetches a live exchange rate from the free Frankfurter API (no key
    # required). Returns None on any failure so the UI can degrade
    # gracefully instead of crashing the whole dashboard over a network
    # hiccup - a live data feed should never be a single point of failure.

    try:
        response = requests.get (
            FX_API_URL,
            params = {"base": base,"symbols": target},
            timeout = 5,
        )
        response.raise_for_status ()
        data = response.json ()
        return {
            "rate": data ["rates"][target],
            "date": data ["date"],
            "base": base,
            "target": target,
        }
    except (requests.RequestException,KeyError,ValueError):
        return None