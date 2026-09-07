# src/clean_data.py

# Day 2: Cleans and preprocesses the raw Global Superstore dataset.

# What this script does:
# 1. Loads the three raw sheets (Orders, Returns, People)
# 2. Standardizes column names to snake_case
# 3. Merges Returns + People into Orders
# 4. Engineers derived columns needed for analysis and the dashboard
# 5. Runs basic data quality checks
# 6. Saves a single clean, analysis-ready file to data/processed/

import os
import pandas as pd

RAW_PATH = "data/raw/global_superstore_2016.xlsx"
PROCESSED_DIR = "data/processed"


def load_raw_sheets ():

    # Load all three sheets from the raw Excel workbook.

    sheets = pd.read_excel (RAW_PATH,sheet_name = None)
    return sheets ["Orders"],sheets ["Returns"],sheets ["People"]

def standardize_columns (df):

    # Convert column names to snake_case for consistent, code-friendly access.

    df = df.copy ()
    df.columns = (
        df.columns
        .str.strip ()
        .str.lower ()
        .str.replace (" ", "_")
        .str.replace ("-", "_")
    )
    return df

def merge_supporting_tables (orders,returns,people):

    # Merge the Returns and People sheets into Orders.

    # - Returns: adds a 'returned' flag (Yes/No) per order
    # - People: adds the regional manager name per region

    # Drop 'region' from returns before merging - orders already has it,
    # and keeping both would create duplicate/suffixed columns

    returns_slim = returns [["order_id","returned"]]

    merged = orders.merge (returns_slim,on = "order_id",how = "left")
    merged ["returned"] = merged ["returned"].fillna ("No")

    # Rename 'person' to something more descriptive before merging

    people = people.rename (columns = {"person": "regional_manager"})
    merged = merged.merge (people,on = "region",how = "left")
    return merged

def engineer_features (df):

    # Add derived columns used throughout the analysis and dashboard.

    df = df.copy ()

    # Guarantee real datetime dtype regardless of how Excel stored it

    df ["order_date"] = pd.to_datetime (df ["order_date"])
    df ["ship_date"] = pd.to_datetime (df ["ship_date"])

    # Operational metric: how many days between order and shipment

    df ["shipping_duration_days"] = (df ["ship_date"] - df ["order_date"]).dt.days

    # Profit margin as a percentage of sales - guard against divide-by-zero

    df ["profit_margin_pct"] = (df ["profit"] / df ["sales"].replace (0,pd.NA)) * 100

    # Time components for grouping and trend charts later

    df ["order_year"] = df ["order_date"].dt.year
    df ["order_month"] = df ["order_date"].dt.month
    df ["order_year_month"] = df ["order_date"].dt.to_period ("M").astype (str)

    return df

def run_quality_checks(df):

    # Print a quick data quality summary - visibility, not a hard gate.

    print ("Row count:",len (df))
    print ("Duplicate rows:",df.duplicated ().sum ())
    print ("Orders with negative sales:", (df ["sales"] < 0).sum ())
    print ("Rows with negative shipping duration:", (df ["shipping_duration_days"] < 0).sum ())

    missing = df.isnull ().sum ()
    print ("\nColumns with missing values:")
    print (missing [missing > 0])

    # Note: postal_code will show missing values for most non-US countries -
    # that's expected, not a data error, since only the US market uses them here

def main ():
    os.makedirs (PROCESSED_DIR,exist_ok = True)

    orders,returns,people = load_raw_sheets ()

    orders = standardize_columns (orders)
    returns = standardize_columns (returns)
    people = standardize_columns (people)

    df = merge_supporting_tables (orders,returns,people)
    df = engineer_features (df)

    run_quality_checks (df)

    output_path = os.path.join (PROCESSED_DIR,"orders_clean.parquet")
    df.to_parquet (output_path,index = False)
    print (f"\nSaved clean dataset to {output_path} !!")
    print ("Final shape:",df.shape)

if __name__ == "__main__":
    main ()