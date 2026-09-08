# tests/test_pipeline.py

# Automated checks for the data pipeline (Days 2-3) and the data contracts
# the dashboard (Day 4) depends on. Not exhaustive - these exist to catch
# the kind of silent breakage we already hit once (the forecast's missing
# "month" column) before it reaches the dashboard or a deployment.

# Run with: pytest tests/test_pipeline.py -v

import pandas as pd
import pytest

ORDERS_PATH = "data/processed/orders_clean.parquet"
RISK_PATH = "data/processed/risk_scores.parquet"
FORECAST_PATH = "data/processed/revenue_forecast.parquet"

@pytest.fixture (scope = "module")
def orders ():
    return pd.read_parquet (ORDERS_PATH)

@pytest.fixture (scope = "module")
def risk_scores ():
    return pd.read_parquet (RISK_PATH)

@pytest.fixture (scope = "module")
def forecast ():
    return pd.read_parquet (FORECAST_PATH)

class TestOrdersData:
    def test_row_count_matches_source (self,orders):

        # The raw Global Superstore Orders sheet has exactly 51,290 rows -
        # cleaning should never add or drop rows, only columns

        assert len (orders) == 51290

    def test_no_duplicate_rows (self,orders):
        assert orders.duplicated ().sum () == 0

    def test_no_negative_sales (self,orders):
        assert (orders ["sales"] < 0).sum () == 0

    def test_regional_manager_has_no_nulls (self,orders):

        # This was the Day 2 bug - Canada sub-regions were left NaN until
        # we explicitly labeled them "Unassigned". Guard against regressing.

        assert orders ["regional_manager"].isnull ().sum () == 0

    def test_required_columns_present (self,orders):
        required = {
            "order_date","ship_date","sales","profit","discount",
            "region","market","category","sub_category","returned",
            "regional_manager","shipping_duration_days","profit_margin_pct",
        }
        assert required.issubset (set(orders.columns))

class TestRiskScores:
    def test_risk_tiers_are_valid (self,risk_scores):

        valid_tiers = {"Healthy","Watch","High risk"}
        assert set(risk_scores ["risk_tier"].unique ()).issubset (valid_tiers)

    def test_negative_margin_is_always_high_risk (self,risk_scores):

        # Core business rule from risk_engine.py - if this breaks, the
        # dashboard's risk flags become actively misleading

        negative_margin = risk_scores [risk_scores ["profit_margin_pct"] < 0]
        assert (negative_margin ["risk_tier"] == "High risk").all ()

    def test_no_duplicate_segments (self,risk_scores):
        duplicates = risk_scores.duplicated (subset = ["sub_category","region"])
        assert duplicates.sum () == 0

class TestForecast:
    def test_month_column_exists (self,forecast):

        # Regression test for the exact bug that crashed the dashboard -
        # must never silently disappear again

        assert "month" in forecast.columns

    def test_actual_and_forecast_columns_exist (self,forecast):

        assert {"actual_revenue","forecast_revenue"}.issubset (set(forecast.columns))

    def test_exactly_six_forecast_months (self,forecast):

        forecast_only = forecast [forecast ["forecast_revenue"].notna ()]
        assert len (forecast_only) == 6

    def test_actual_and_forecast_do_not_overlap (self,forecast):

        # Every row should have exactly one of the two populated, never
        # both - a month can't be simultaneously historical fact and prediction

        both_populated = forecast [
            forecast ["actual_revenue"].notna () & forecast ["forecast_revenue"].notna ()
        ]
        assert len (both_populated) == 0