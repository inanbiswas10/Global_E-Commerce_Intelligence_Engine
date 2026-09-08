# app/theme.py

# Design system for the Global E-Commerce Intelligence Engine dashboard.

# Palette concept: a night trading-floor / world-market view rather than a
# generic light SaaS dashboard - deep indigo base, warm gold accent (tied to
# currency/commodity trading), with risk-tier colors (emerald/gold/coral)
# reused directly from the Day 3 risk engine so the color system carries
# real meaning instead of being decorative.

# Typography: IBM Plex Sans for headings and body text, IBM Plex Mono for
# every number on the page (KPIs, table figures) - a deliberate ledger/
# precision feel rather than a generic monospace label.

import streamlit as st

COLORS = {
    "bg": "#0F1729",
    "surface": "#182238",
    "surface_alt": "#1F2C47",
    "border": "#2A3652",
    "text_primary": "#F2EFE9",
    "text_secondary": "#8A93A6",
    "accent": "#E8A33D",     # gold - brand accent, also the "Watch" risk tier
    "profit": "#2DB88A",     # emerald - "Healthy" tier / positive figures
    "risk": "#E8604C",       # coral - "High risk" tier / negative figures
}

RISK_TIER_COLORS = {
    "Healthy": COLORS ["profit"],
    "Watch": COLORS ["accent"],
    "High risk": COLORS ["risk"],
}

def inject_theme ():

    # Injects fonts and CSS overrides. Call once, at the top of app/main.py.

    st.markdown (
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

        :root {{
            --bg: {COLORS ["bg"]};
            --surface: {COLORS ["surface"]};
            --surface-alt: {COLORS ["surface_alt"]};
            --border: {COLORS ["border"]};
            --text-primary: {COLORS ["text_primary"]};
            --text-secondary: {COLORS ["text_secondary"]};
            --accent: {COLORS ["accent"]};
            --profit: {COLORS ["profit"]};
            --risk: {COLORS ["risk"]};
        }}

        /* Base app surface and typography */
        .stApp {{
            background-color: var(--bg);
            font-family: 'IBM Plex Sans', sans-serif;
            color: var(--text-primary);
        }}

        /* FIX: Streamlit's own top toolbar (where "Deploy" sits) defaults
           to a different dark shade than our background, creating a
           visible seam at the very top of the page. Force it to match. */
        [data-testid="stHeader"] {{
            background-color: var(--bg);
        }}

        h1, h2, h3, h4 {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-weight: 600;
            color: var(--text-primary);
            letter-spacing: -0.01em;
        }}

        p, span, div, label {{
            font-family: 'IBM Plex Sans', sans-serif;
        }}

        [data-testid="stSidebar"] {{
            background-color: var(--surface);
            border-right: 1px solid var(--border);
        }}
        [data-testid="stSidebar"] * {{
            color: var(--text-primary);
        }}

        .section-heading {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--text-primary);
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
            margin: 2rem 0 1rem 0;
        }}

        .hero-wordmark {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.85rem;
            letter-spacing: 0.04em;
            color: var(--accent);
            margin-bottom: 0.25rem;
        }}
        .hero-title {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 2.1rem;
            font-weight: 700;
            color: var(--text-primary);
            margin: 0 0 0.3rem 0;
            line-height: 1.15;
            max-width: 820px;
        }}
        .hero-subtitle {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.95rem;
            color: var(--text-secondary);
            max-width: 640px;
        }}

        .fx-ticker {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.8rem;
            color: var(--text-secondary);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 0.5rem 0.9rem;
            display: inline-block;
        }}
        .fx-ticker .fx-live-dot {{
            display: inline-block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: var(--profit);
            margin-right: 6px;
        }}
        .fx-ticker .fx-value {{
            color: var(--text-primary);
            font-weight: 500;
        }}

        .ledger-strip {{
            display: flex;
            border-top: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
            margin: 1.5rem 0;
        }}
        .ledger-item {{
            flex: 1;
            padding: 1rem 1.25rem;
            border-right: 1px solid var(--border);
        }}
        .ledger-item:last-child {{
            border-right: none;
        }}
        .ledger-label {{
            font-family: 'IBM Plex Sans', sans-serif;
            font-size: 0.78rem;
            color: var(--text-secondary);
            margin-bottom: 0.35rem;
        }}
        .ledger-value {{
            font-family: 'IBM Plex Mono', monospace;
            font-size: 1.5rem;
            font-weight: 500;
            color: var(--text-primary);
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid var(--border);
            border-radius: 4px;
        }}

        [data-baseweb="select"] {{
            border-color: var(--border) !important;
        }}
        </style>
        """,
        unsafe_allow_html = True,
    )