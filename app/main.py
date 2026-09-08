# app/main.py

# Global E-Commerce Intelligence Engine - main Streamlit application.

# Day 4 Part B: adds the revenue trend/forecast chart, market performance,
# sub-category profitability, the discount-vs-profit scatter, and the risk
# watchlist table beneath the Part A header and KPI strip.

import streamlit as st
from theme import COLORS,inject_theme
from data_loader import load_orders,load_risk_scores,load_forecast,fetch_live_fx_rate
from charts import (
    revenue_trend_chart,
    market_performance_chart,
    subcategory_profit_chart,
    discount_vs_profit_chart,
    risk_watchlist_html,
)

# --- Page setup ---

st.set_page_config (
    page_title = "Global E-Commerce Intelligence Engine",
    page_icon = "🌐",
    layout = "wide",
    initial_sidebar_state = "expanded",
)
inject_theme ()

# --- Load data ---

orders = load_orders ()
risk_scores = load_risk_scores ()
forecast = load_forecast ()

# --- Sidebar filters ---

st.sidebar.markdown ("### Filters")

markets = sorted (orders ["market"].unique ().tolist ())
selected_markets = st.sidebar.multiselect (
    "Market",options = markets,default = markets)

categories = sorted (orders ["category"].unique ().tolist ())
selected_categories = st.sidebar.multiselect (
    "Category",options = categories,default = categories)

year_min = int (orders ["order_year"].min ())
year_max = int (orders ["order_year"].max ())
selected_years = st.sidebar.slider (
    "Order year",min_value = year_min,max_value = year_max,
    value = (year_min,year_max),
)

filtered_orders = orders [
    orders ["market"].isin (selected_markets)
    & orders ["category"].isin (selected_categories)
    & orders ["order_year"].between (selected_years [0],selected_years [1])
]

st.sidebar.markdown ("---")
st.sidebar.markdown (
    f"<span style='color:{COLORS ['text_secondary']}; font-size:0.8rem;'>"
    f"{len (filtered_orders):,} of {len (orders):,} orders shown</span>",
    unsafe_allow_html = True,
)

# --- Header ---

fx = fetch_live_fx_rate (base = "USD",target = "EUR")

header_col,ticker_col = st.columns ([3,1])

with header_col:
    st.markdown (
        """
        <div class="hero-wordmark">GLOBAL E-COMMERCE INTELLIGENCE ENGINE</div>
        <div class="hero-title">Where the business is making money & where it isn't -</div>
        <div class="hero-subtitle">
            51,290 orders across 23 regions during the period of 2012–2015. Profit-risk scoring
            and a revenue forecast built directly on top of the raw
            transaction data.
        </div>
        """,
        unsafe_allow_html = True,
    )

with ticker_col:
    if fx is not None:
        ticker_html = f"""
        <div class="fx-ticker">
            <span class="fx-live-dot"></span>Live Rate ({fx ['date']})<br>
            1 {fx ['base']} = <span class="fx-value">{fx ['rate']:.4f} {fx ['target']}</span>
        </div>
        """
    else:
        ticker_html = """
        <div class="fx-ticker">FX Rate Unavailable Right Now</div>
        """
    st.markdown (ticker_html,unsafe_allow_html = True)

# --- KPI ledger strip ---

total_revenue = filtered_orders ["sales"].sum ()
total_profit = filtered_orders ["profit"].sum ()
margin_pct = (total_profit/total_revenue * 100) if total_revenue else 0
order_count = filtered_orders ["order_id"].nunique ()
high_risk_count = (risk_scores ["risk_tier"] == "High risk").sum ()

forecast_sorted = forecast.sort_values ("month")
future_rows = forecast_sorted.loc [forecast_sorted ["forecast_revenue"].notna (),"forecast_revenue"]
next_month_value = future_rows.iloc [0] if len (future_rows) else None

ledger_html = f"""
<div class="ledger-strip">
    <div class="ledger-item">
        <div class="ledger-label">Total Revenue</div>
        <div class="ledger-value">${total_revenue:,.0f}</div>
    </div>
    <div class="ledger-item">
        <div class="ledger-label">Total Profit</div>
        <div class="ledger-value">${total_profit:,.0f}</div>
    </div>
    <div class="ledger-item">
        <div class="ledger-label">Profit Margin</div>
        <div class="ledger-value">{margin_pct:.1f} %</div>
    </div>
    <div class="ledger-item">
        <div class="ledger-label">Orders</div>
        <div class="ledger-value">{order_count:,}</div>
    </div>
    <div class="ledger-item">
        <div class="ledger-label">High-Risk Segments</div>
        <div class="ledger-value" style="color:{COLORS ['risk']};">{high_risk_count}</div>
    </div>
    <div class="ledger-item">
        <div class="ledger-label">Next Month Forecast</div>
        <div class="ledger-value">{f"${next_month_value:,.0f}" if next_month_value else "—"}</div>
    </div>
</div>
"""
st.markdown (ledger_html,unsafe_allow_html = True)

# --- Revenue trend & forecast ---

st.markdown (
    "<div class='section-heading'>Revenue Trend &amp; Forecast</div>",
    unsafe_allow_html = True,
)
st.plotly_chart (
    revenue_trend_chart (forecast),
    use_container_width = True,
    config = {"displayModeBar": False},
)

# --- Market performance + sub-category profitability, side by side ---

st.markdown (
    "<div class='section-heading'>Where the money is & where it isn't -</div>",
    unsafe_allow_html = True,
)
chart_col1,chart_col2 = st.columns (2)

with chart_col1:
    st.plotly_chart (
        market_performance_chart (filtered_orders),
        use_container_width = True,
        config = {"displayModeBar": False},
    )

with chart_col2:
    st.plotly_chart (
        subcategory_profit_chart (filtered_orders),
        use_container_width = True,
        config = {"displayModeBar": False},
    )

# --- Discount impact ---

st.markdown (
    "<div class='section-heading'>Does discounting actually pay off ??</div>",
    unsafe_allow_html = True,
)
st.plotly_chart (
    discount_vs_profit_chart (filtered_orders),
    use_container_width = True,
    config = {"displayModeBar": False},
)

# --- Risk watchlist ---

st.markdown (
    "<div class='section-heading'>Risk Watchlist — 15 Worst Performing Segments</div>",
    unsafe_allow_html = True,
)
st.markdown (risk_watchlist_html (risk_scores,limit = 15),unsafe_allow_html = True)

with st.expander (f"View Full Risk Table — All {len (risk_scores)} Segments"):
    st.dataframe (
        risk_scores.sort_values ("total_profit"),
        use_container_width = True,
        hide_index = True,
    )