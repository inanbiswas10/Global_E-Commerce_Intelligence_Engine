# src/risk_engine.py

# Day 3 Part A: Profit-risk scoring engine.

# Turns the Day 2 EDA finding (discount-driven margin loss, not returns,
# is the real risk signal) into a reusable scoring engine. Scores every
# (sub_category, region) combination and classifies it into a risk tier,
# so the dashboard can flag exactly where the business is losing money.

import pandas as pd

INPUT_PATH = "data/processed/orders_clean.parquet"
OUTPUT_PATH = "data/processed/risk_scores.parquet"

# Risk tier thresholds - tuned from what Day 2's EDA actually showed,
# not arbitrary guesses.

MARGIN_HIGH_RISK = 0.0     # negative margin = actively losing money
MARGIN_WATCH = 11.61       # matches the overall portfolio margin from Day 2 -
                            # below-average segments get flagged for review
DISCOUNT_WATCH = 0.20      # 20%+ average discount is a red flag on its own


def load_clean_data():
    return pd.read_parquet(INPUT_PATH)


def aggregate_by_segment(df):
  
    """
    Aggregate metrics per (sub_category, region) - finer-grained than
    Day 2's sub_category-only view, so regional pockets of risk inside
    an otherwise healthy sub-category don't get averaged away.
    """
    grouped = df.groupby(["sub_category", "region"], as_index=False).agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        avg_discount=("discount", "mean"),
        order_count=("order_id", "nunique"),
    )

    # Guard against divide-by-zero for segments with zero sales
    grouped["profit_margin_pct"] = (
        grouped["total_profit"] / grouped["total_sales"].replace(0, pd.NA)
    ) * 100

    return grouped


def score_risk(row):
    """
    Assigns a risk tier based on profit margin and discount level.

    High risk - actively losing money (negative margin)
    Watch     - positive but below-average margin, or discount-heavy
    Healthy   - solid margin, discounting isn't eroding profit
    """
    if row["profit_margin_pct"] < MARGIN_HIGH_RISK:
        return "High risk"
    if row["profit_margin_pct"] < MARGIN_WATCH or row["avg_discount"] >= DISCOUNT_WATCH:
        return "Watch"
    return "Healthy"


def main():
    df = load_clean_data()
    segments = aggregate_by_segment(df)

    segments["risk_tier"] = segments.apply(score_risk, axis=1)

    # Sort so the worst offenders surface first - this order feeds
    # directly into the dashboard's "top risks" table in Day 4
    segments = segments.sort_values("total_profit")

    print("Risk tier counts:")
    print(segments["risk_tier"].value_counts())

    print("\nTop 5 highest-risk segments (most negative profit first):")
    print(
        segments[segments["risk_tier"] == "High risk"]
        .head(5)
        .to_string(index=False)
    )

    segments.to_parquet(OUTPUT_PATH, index=False)
    print(f"\nSaved risk scores to {OUTPUT_PATH}")
    print("Shape:", segments.shape)


if __name__ == "__main__":
    main()