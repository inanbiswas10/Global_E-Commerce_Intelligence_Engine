"""
src/forecast_engine.py

Day 3 Part B: Revenue forecasting engine.

Fits a Holt-Winters (triple exponential smoothing) model to monthly
revenue - a standard, explainable approach for retail data that has
both a trend and yearly seasonality (holiday-season spikes). Forecasts
the next 6 months for the dashboard's trend chart.
"""

import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

INPUT_PATH = "data/processed/orders_clean.parquet"
OUTPUT_PATH = "data/processed/revenue_forecast.parquet"
FORECAST_MONTHS = 6


def load_monthly_revenue():
    """Aggregate cleaned orders into a monthly revenue time series."""
    df = pd.read_parquet(INPUT_PATH)

    monthly = (
        df.groupby(pd.Grouper(key="order_date", freq="MS"))["sales"]
        .sum()
        .asfreq("MS")  # explicit monthly frequency - required for forecasting
        .rename("actual_revenue")
    )
    return monthly


def fit_and_forecast(monthly_series):
    """
    Fits Holt-Winters with additive trend and additive yearly (12-month)
    seasonality, then forecasts FORECAST_MONTHS ahead.
    """
    model = ExponentialSmoothing(
        monthly_series,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
    )
    fitted_model = model.fit()

    forecast = fitted_model.forecast(FORECAST_MONTHS)
    forecast.name = "forecast_revenue"

    return fitted_model, forecast


def main():
    monthly = load_monthly_revenue()
    print(
        f"Monthly revenue series: {len(monthly)} months "
        f"({monthly.index.min().date()} to {monthly.index.max().date()})"
    )

    fitted_model, forecast = fit_and_forecast(monthly)

    print("\nForecast for the next 6 months:")
    print(forecast.round(2).to_string())

    # Combine actuals and forecast into one tidy table for the dashboard -
    # actual_revenue is NaN for future months, forecast_revenue is NaN
    # for past months, so the chart can plot both series cleanly
    combined = pd.concat([monthly, forecast], axis=1).reset_index()
    combined = combined.rename(columns={"order_date": "month"})

    combined.to_parquet(OUTPUT_PATH, index=False)
    print(f"\nSaved forecast to {OUTPUT_PATH}")
    print("Shape:", combined.shape)


if __name__ == "__main__":
    main()