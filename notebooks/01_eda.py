# %% [markdown]
# # Day 2 Part B — Exploratory Data Analysis
# **Global E-Commerce Intelligence Engine — Global Superstore dataset**
#
# This explores the cleaned dataset (`data/processed/orders_clean.parquet`)
# to surface the patterns that will shape the core engine (Day 3) and the
# dashboard (Day 4). Run cells individually in VS Code's Interactive Window,
# or run the whole file as a script.

# %%
import pandas as pd
import plotly.express as px

# A consistent color palette so every chart in this project looks like
# it belongs together - we'll reuse this exact list in the dashboard later
PALETTE = ["#1D9E75", "#378ADD", "#D85A30", "#D4537E", "#7F77DD", "#BA7517"]

df = pd.read_parquet("data/processed/orders_clean.parquet")
print("Loaded:", df.shape)

# %% [markdown]
# ## 1. Overview KPIs

# %%
total_revenue = df["sales"].sum()
total_profit = df["profit"].sum()
total_orders = df["order_id"].nunique()
overall_margin = (total_profit / total_revenue) * 100
date_min = df["order_date"].min().date()
date_max = df["order_date"].max().date()

print(f"Total revenue:         ${total_revenue:,.2f}")
print(f"Total profit:          ${total_profit:,.2f}")
print(f"Overall profit margin:  {overall_margin:.2f}%")
print(f"Unique orders:          {total_orders:,}")
print(f"Date range:             {date_min} to {date_max}")

# %% [markdown]
# ## 2. Revenue and profit by market
# Shows which global markets drive revenue vs. which actually convert
# that revenue into profit - these are not always the same market.

# %%
by_market = (
    df.groupby("market", as_index=False)
    .agg(total_sales=("sales", "sum"), total_profit=("profit", "sum"))
    .sort_values("total_sales", ascending=False)
)

fig_market = px.bar(
    by_market,
    x="market",
    y=["total_sales", "total_profit"],
    barmode="group",
    title="Revenue vs. profit by market",
    color_discrete_sequence=PALETTE,
    labels={"value": "USD", "market": "Market", "variable": "Metric"},
)
fig_market.show()

# %% [markdown]
# ## 3. Monthly revenue trend
# A time series view - useful for spotting seasonality and growth.

# %%
monthly = (
    df.groupby("order_year_month", as_index=False)["sales"]
    .sum()
    .sort_values("order_year_month")
)

fig_trend = px.line(
    monthly,
    x="order_year_month",
    y="sales",
    title="Monthly revenue trend",
    color_discrete_sequence=PALETTE,
    labels={"order_year_month": "Month", "sales": "Revenue (USD)"},
)
fig_trend.update_xaxes(tickangle=45, nticks=20)
fig_trend.show()

# %% [markdown]
# ## 4. Top and bottom sub-categories by profit
# Some product lines quietly lose money even while selling well - this
# is exactly the kind of insight that makes an "intelligence engine"
# useful rather than just decorative.

# %%
by_subcat = (
    df.groupby("sub_category", as_index=False)["profit"]
    .sum()
    .sort_values("profit")
)

fig_subcat = px.bar(
    by_subcat,
    x="profit",
    y="sub_category",
    orientation="h",
    title="Total profit by sub-category",
    color="profit",
    color_continuous_scale=["#D85A30", "#F0997B", "#5DCAA5", "#1D9E75"],
    labels={"profit": "Total profit (USD)", "sub_category": "Sub-category"},
)
fig_subcat.show()

print("\nLowest-profit sub-categories:")
print(by_subcat.head(3).to_string(index=False))

# %% [markdown]
# ## 5. Discount vs. profit
# The classic question: does discounting actually pay off, or does it
# erode margin past the point of usefulness?

# %%
fig_discount = px.scatter(
    df.sample(5000, random_state=42),  # sample for a readable plot
    x="discount",
    y="profit",
    color="category",
    title="Discount vs. profit (5,000-order sample)",
    color_discrete_sequence=PALETTE,
    labels={"discount": "Discount rate", "profit": "Profit (USD)"},
    opacity=0.6,
)
fig_discount.add_hline(y=0, line_dash="dash", line_color="gray")
fig_discount.show()

# %% [markdown]
# ## 6. Return rate by category
# What share of orders in each category come back?

# %%
return_rate = (
    df.groupby("category", as_index=False)
    .agg(
        total_orders=("order_id", "count"),
        returned_orders=("returned", lambda s: (s == "Yes").sum()),
    )
)
return_rate["return_rate_pct"] = (
    return_rate["returned_orders"] / return_rate["total_orders"]
) * 100

fig_returns = px.bar(
    return_rate.sort_values("return_rate_pct", ascending=False),
    x="category",
    y="return_rate_pct",
    title="Return rate by category",
    color_discrete_sequence=PALETTE,
    labels={"return_rate_pct": "Return rate (%)", "category": "Category"},
)
fig_returns.show()

print(return_rate.to_string(index=False))