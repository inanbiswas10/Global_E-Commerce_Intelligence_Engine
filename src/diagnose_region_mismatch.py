# src/diagnose_region_mismatch.py

# One-off diagnostic: finds out exactly why 384 orders ended up with a
# missing regional_manager after merging the People sheet into Orders
# on 'region'. Run once, read the output, then we fix clean_data.py
# based on what it shows - no guessing.

import pandas as pd

RAW_PATH = "data/raw/global_superstore_2016.xlsx"

def standardize_columns (df):

    # Same standardization used in clean_data.py, kept identical on purpose.

    df = df.copy ()
    df.columns = (
        df.columns
        .str.strip ()
        .str.lower ()
        .str.replace (" ", "_")
        .str.replace ("-", "_")
    )
    return df

def main ():
    sheets = pd.read_excel (RAW_PATH,sheet_name = None)
    orders = standardize_columns (sheets ["Orders"])
    people = standardize_columns (sheets ["People"])

    order_regions = set(orders ["region"].dropna ().unique ())
    people_regions = set(people ["region"].dropna ().unique ())

    print ("Distinct regions in Orders:",len (order_regions))
    print ("Distinct regions in People:",len (people_regions))

    # Regions that exist in Orders but have no matching People entry -
    # these are exactly what's causing the 384 missing managers\

    only_in_orders = order_regions - people_regions
    print ("\nRegions in Orders with NO match in People:")
    for region in sorted (only_in_orders):
        count = (orders ["region"] == region).sum ()
        print (f"  '{region}'  ->  {count} orders")

    # Regions that exist in People but are never used in Orders - harmless,
    # just tells us if there's a naming mismatch (e.g. 'EMEA' vs 'Emea')

    only_in_people = people_regions - order_regions
    print ("\nRegions in People with NO match in Orders (check for typos here):")
    for region in sorted (only_in_people):
        print (f"  '{region}'")

if __name__ == "__main__":
    main ()