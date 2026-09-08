# app/charts.py

# Reusable Plotly chart builders for the dashboard. Every chart is passed
# through apply_dark_theme() so the whole dashboard reads as one coherent
# system, instead of Plotly's default light-themed charts sitting awkwardly
# on our dark background.

import plotly.express as px
import plotly.graph_objects as go
from theme import COLORS,RISK_TIER_COLORS

CATEGORICAL_PALETTE = [
    COLORS ["accent"],COLORS ["profit"],COLORS ["risk"],
    "#5B8DEF", "#B48EAD", "#7FB3B0",
]

def apply_dark_theme (fig,title = None):

    # Applies the dashboard's shared Plotly styling to any figure.

    fig.update_layout (
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor = "rgba(0,0,0,0)",
        font = dict(family = "IBM Plex Sans, sans-serif",color = COLORS ["text_secondary"],size = 13),
        title = dict(text = title,font = dict(color = COLORS ["text_primary"],size = 15)) if title else None,
        margin = dict(l = 10,r = 10,t = 40 if title else 10,b = 10),
        legend = dict(bgcolor = "rgba(0,0,0,0)",font = dict(color = COLORS ["text_secondary"])),
    )
    fig.update_xaxes (gridcolor = COLORS ["border"],zerolinecolor = COLORS ["border"])
    fig.update_yaxes (gridcolor = COLORS ["border"],zerolinecolor = COLORS ["border"])
    return fig

def revenue_trend_chart (forecast_df):

    # Actual monthly revenue with the 6-month forecast as a dashed continuation.

    fig = go.Figure ()

    fig.add_trace (go.Scatter (
        x = forecast_df ["month"],y = forecast_df ["actual_revenue"],
        mode = "lines",name = "Actual Revenue",
        line = dict(color = COLORS ["profit"],width = 2.5),
    ))
    fig.add_trace (go.Scatter (
        x = forecast_df ["month"],y = forecast_df ["forecast_revenue"],
        mode = "lines",name = "Forecast",
        line = dict(color = COLORS ["accent"],width = 2.5,dash = "dash"),
    ))
    return apply_dark_theme (fig,title = "Monthly Revenue — Actual vs 6-Month Forecast")

def market_performance_chart (filtered_orders):

    # Grouped bar: revenue vs profit by market.

    by_market = (
        filtered_orders.groupby ("market",as_index = False)
        .agg (total_sales = ("sales","sum"),total_profit = ("profit","sum"))
        .sort_values ("total_sales",ascending = False)
    )

    fig = go.Figure ()
    fig.add_trace (go.Bar (
        x = by_market ["market"],y = by_market ["total_sales"],
        name = "Revenue",marker_color = COLORS ["accent"],
    ))
    fig.add_trace (go.Bar (
        x = by_market ["market"],y = by_market ["total_profit"],
        name = "Profit",marker_color = COLORS ["profit"],
    ))
    fig.update_layout (barmode = "group")
    return apply_dark_theme (fig,title = "Revenue vs Profit By Market")

def subcategory_profit_chart (filtered_orders):

    # Horizontal bar of profit by sub-category, colored red for any net loss.

    by_subcat = (
        filtered_orders.groupby ("sub_category",as_index = False)["profit"]
        .sum ()
        .sort_values ("profit")
    )
    bar_colors = [COLORS ["risk"] if v < 0 else COLORS ["profit"] for v in by_subcat ["profit"]]

    fig = go.Figure (go.Bar (
        x = by_subcat ["profit"],y = by_subcat ["sub_category"],
        orientation = "h",marker_color = bar_colors,))

    return apply_dark_theme (fig,title = "Profit By Sub-Category")

def discount_vs_profit_chart (filtered_orders,sample_size = 4000):

    # Scatter of discount rate vs profit, sampled for a readable render.

    sample = filtered_orders.sample (
        min (sample_size,len (filtered_orders)),random_state = 42)

    fig = px.scatter (
        sample,x = "discount",y = "profit",color = "category",
        color_discrete_sequence = CATEGORICAL_PALETTE,opacity = 0.55,
    )
    fig.add_hline (y = 0,line_dash = "dash",line_color = COLORS ["text_secondary"])

    return apply_dark_theme (fig,title = "Discount Rate vs Profit")

def risk_watchlist_html (risk_df,limit = 15):

    # Builds a styled HTML table for the highest-risk segments - a custom
    # "watchlist" look with a colored left-border stripe per risk tier.

    # FIX: built as single-line HTML strings with zero internal newlines
    # on purpose. Streamlit's markdown renderer falls back to showing raw
    # text instead of rendering HTML as soon as it hits 4+ spaces of
    # indentation or a blank/whitespace-only line - which is exactly what
    # the previous multi-line, indented version accidentally produced when
    # the row strings got concatenated in a loop. A single unbroken line
    # sidesteps that failure mode entirely.

    worst = risk_df.sort_values ("total_profit").head (limit)
    text_secondary = COLORS ["text_secondary"]
    text_primary = COLORS ["text_primary"]
    border = COLORS ["border"]

    row_lines = []
    for _, row in worst.iterrows ():
        stripe_color = RISK_TIER_COLORS.get (row ["risk_tier"],text_secondary)
        profit_color = COLORS ["risk"] if row ["total_profit"] < 0 else text_primary

        cells = (
            f'<td style="padding:0.6rem 0.9rem; color:{text_primary};">{row ["sub_category"]}</td>'
            f'<td style="padding:0.6rem 0.9rem; color:{text_secondary};">{row ["region"]}</td>'
            f'<td style="padding:0.6rem 0.9rem; font-family:\'IBM Plex Mono\',monospace; color:{profit_color};">${row ["total_profit"]:,.0f}</td>'
            f'<td style="padding:0.6rem 0.9rem; font-family:\'IBM Plex Mono\',monospace; color:{text_secondary};">{row ["avg_discount"] * 100:.0f} %</td>'
            f'<td style="padding:0.6rem 0.9rem; color:{stripe_color}; font-weight:500;">{row ["risk_tier"]}</td>'
        )
        row_lines.append (f'<tr style="border-left:3px solid {stripe_color};">{cells}</tr>')

    rows_html = "".join (row_lines)

    header_cells = "".join (
        f'<th style="text-align:left; padding:0.5rem 0.9rem; color:{text_secondary}; font-weight:500;">{label}</th>'
        for label in ["Sub-Category", "Region", "Total profit", "Avg. discount", "Tier"]
    )
    header_html = f'<tr style="border-bottom:1px solid {border};">{header_cells}</tr>'

    table_html = (
        '<table style="width:100%; border-collapse:collapse; '
        'font-family:\'IBM Plex Sans\',sans-serif; font-size:0.85rem;">'
        f'<thead>{header_html}</thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table>'
    )
    return table_html