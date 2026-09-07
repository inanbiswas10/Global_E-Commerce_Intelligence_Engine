# src/verify_data.py

# Quick sanity check for Day 1: confirms the Global Superstore dataset
# downloaded correctly and gives a first look at its shape, columns, and
# (if applicable) sheets. This is not cleaning — just verification.

import os
import pandas as pd

# IMPORTANT: update this to match the exact filename you saw in data/raw
# (Kaggle ships this dataset as either .csv or .xlsx depending on the upload)

DATA_PATH = "data/raw/global_superstore_2016.xlsx"

def main ():

    # Detect the file type so this script works whether you got a CSV
    # or an Excel workbook

    extension = os.path.splitext (DATA_PATH)[1].lower ()

    if extension in (".xlsx",".xls"):

        # The classic Global Superstore workbook ships with 3 sheets:
        # Orders, Returns, and People — read all of them at once

        sheets = pd.read_excel (DATA_PATH,sheet_name = None)

        for sheet_name,df in sheets.items ():

            print (f"\n--- Sheet: {sheet_name} ---")
            print ("Shape (rows, columns):", df.shape)
            print ("Columns:", df.columns.tolist ())
    else:
        # Most Global Superstore CSVs on Kaggle need latin-1 encoding
        # because of special characters in country and city names

        df = pd.read_csv (DATA_PATH,encoding = "latin-1")

        print ("Shape (rows, columns):",df.shape)
        print ("\nColumns:")
        print (df.columns.tolist ())

        print ("\nFirst 5 rows:")
        print (df.head ())

        print ("\nMissing values per column (only columns with gaps):")
        missing = df.isnull ().sum ()
        print (missing [missing > 0])

if __name__ == "__main__":
    main ()