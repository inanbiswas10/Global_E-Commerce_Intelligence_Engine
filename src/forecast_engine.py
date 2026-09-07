"""
src/forecast_engine.py

Day 3 Part B: Revenue forecasting engine.

Fits a Holt-Winters (triple exponential smoothing) model to monthly
revenue - a standard, explainable approach for retail data that has
both a trend and yearly seasonality (holiday-season spikes). Forecasts
the next 6 months for the dashboard's trend chart, then sanity-checks
the forecast against the same calendar month one year earlier before
trusting it.
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


def sanity_check_forecast(monthly_series, forecast):
    """
    Compares each forecasted month to the same calendar month one year
    earlier. A trustworthy forecast shows a plausible, roughly consistent
    year-over-year growth rate across all 6 months - wild or inconsistent
    swings would suggest the trend component is over-extrapolating from
    only 4 years of history, and the dashboard shouldn't present it as-is.
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
                "WARNING: growth rate is inconsistent month to month - "
                "the model may be over-fitting the trend. Consider "
                "multiplicative seasonality or a longer history."
            )
        else:
            print("Growth rate is reasonably consistent - forecast looks trustworthy.")


def main():
    monthly = load_monthly_revenue()
    print(
        f"Monthly revenue series: {len(monthly)} months "
        f"({monthly.index.min().date()} to {monthly.index.max().date()})"
    )

    fitted_model, forecast = fit_and_forecast(monthly)

    print("\nForecast for the next 6 months:")
    print(forecast.round(2).to_string())

    sanity_check_forecast(monthly, forecast)

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