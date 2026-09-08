"""
src/forecast_engine.py

Day 3 Part B: Revenue forecasting engine.

Fits several Holt-Winters configurations to monthly revenue and picks
the best one using AIC (a standard model-selection criterion) rather
than manually tuning toward a forecast that "looks right" - that would
bias the result. The winning model is then sanity-checked against
year-over-year growth before being trusted for the dashboard.
"""

import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

INPUT_PATH = "data/processed/orders_clean.parquet"
OUTPUT_PATH = "data/processed/revenue_forecast.parquet"
FORECAST_MONTHS = 6

# Candidate configurations to compare. Multiplicative seasonal is included
# because revenue is growing over time - a seasonal swing that scales with
# revenue level is more realistic than one that stays a fixed dollar amount.
# Damped trend is included to avoid over-extrapolating a 4-year trend.
CANDIDATE_CONFIGS = [
    {"label": "Additive trend, additive seasonal",
     "trend": "add", "seasonal": "add", "damped_trend": False},
    {"label": "Additive trend (damped), additive seasonal",
     "trend": "add", "seasonal": "add", "damped_trend": True},
    {"label": "Additive trend, multiplicative seasonal",
     "trend": "add", "seasonal": "mul", "damped_trend": False},
    {"label": "Additive trend (damped), multiplicative seasonal",
     "trend": "add", "seasonal": "mul", "damped_trend": True},
]


def load_monthly_revenue():
    """Aggregate cleaned orders into a monthly revenue time series."""
    df = pd.read_parquet(INPUT_PATH)

    monthly = (
        df.groupby(pd.Grouper(key="order_date", freq="MS"))["sales"]
        .sum()
        .asfreq("MS")
        .rename("actual_revenue")
    )
    return monthly


def select_best_model(monthly_series):
    """
    Fits each candidate config and selects the one with the lowest AIC
    (Akaike Information Criterion) - a standard statistical measure of
    fit quality that penalizes unnecessary complexity. This keeps model
    choice objective instead of picking whichever forecast looks nicest.
    """
    results = []

    for config in CANDIDATE_CONFIGS:
        model = ExponentialSmoothing(
            monthly_series,
            trend=config["trend"],
            seasonal=config["seasonal"],
            seasonal_periods=12,
            damped_trend=config["damped_trend"],
        )
        fitted = model.fit()
        results.append(
            {"label": config["label"], "fitted_model": fitted, "aic": fitted.aic}
        )

    print("Model comparison (lower AIC = better fit):")
    for r in sorted(results, key=lambda r: r["aic"]):
        print(f"  {r['label']:<50} AIC = {r['aic']:.1f}")

    best = min(results, key=lambda r: r["aic"])
    print(f"\nSelected model: {best['label']}")

    return best["fitted_model"]


def sanity_check_forecast(monthly_series, forecast):
    """
    Compares each forecasted month to the same calendar month one year
    earlier. Flags inconsistent YoY growth as a caveat rather than
    hiding it - a forecast can still be useful for the dashboard even
    with some spread, as long as that uncertainty is disclosed rather
    than presented as false precision.
    """
    print("\nSanity check - forecast vs. same month, prior year:")
    growth_rates = []

    for forecast_date, forecast_value in forecast.items():
        prior_year_date = forecast_date - pd.DateOffset(years=1)
        if prior_year_date not in monthly_series.index:
            continue

        prior_value = monthly_series.loc[prior_year_date]
        growth_pct = ((forecast_value - prior_value) / prior_value) * 100
        growth_rates.append(growth_pct)

        print(
            f"  {forecast_date.date()}: forecast ${forecast_value:,.0f}  "
            f"vs {prior_year_date.date()} actual ${prior_value:,.0f}  "
            f"({growth_pct:+.1f}% YoY)"
        )

    if growth_rates:
        spread = max(growth_rates) - min(growth_rates)
        print(f"\nYoY growth spread across the 6 months: {spread:.1f} percentage points")
        if spread > 40:
            print(
                "NOTE: spread is still wide. With only 4 years of history, "
                "some YoY variance is expected and genuine (e.g. holiday "
                "timing shifts) rather than a modeling error. The dashboard "
                "should present this forecast as directional, not precise."
            )
        else:
            print("Growth rate is reasonably consistent - forecast looks trustworthy.")


def main():
    monthly = load_monthly_revenue()
    print(
        f"Monthly revenue series: {len(monthly)} months "
        f"({monthly.index.min().date()} to {monthly.index.max().date()})"
    )

    fitted_model = select_best_model(monthly)

    forecast = fitted_model.forecast(FORECAST_MONTHS)
    forecast.name = "forecast_revenue"

    print("\nForecast for the next 6 months:")
    print(forecast.round(2).to_string())

    sanity_check_forecast(monthly, forecast)

    combined = pd.concat([monthly, forecast], axis=1).reset_index()
    combined = combined.rename(columns={"order_date": "month"})

    combined.to_parquet(OUTPUT_PATH, index=False)
    print(f"\nSaved forecast to {OUTPUT_PATH}")
    print("Shape:", combined.shape)


if __name__ == "__main__":
    main()