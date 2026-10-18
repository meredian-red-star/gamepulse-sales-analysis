"""Clean the sales dataset without changing the original CSV.

Run from the repository root with: python scripts/clean_data.py
Requires pandas.
"""

from pathlib import Path

import pandas as pd


def main():
    # Locate the data folder relative to this script.
    project_folder = Path(__file__).resolve().parent.parent
    input_file = project_folder / "data" / "vgsales.csv"
    output_file = project_folder / "data" / "vgsales_clean.csv"

    sales = pd.read_csv(input_file)
    rows_before = len(sales)

    # Remove only rows with a missing release year.
    cleaned_sales = sales.dropna(subset=["Year"]).copy()

    # Replace missing publishers in the remaining rows.
    publishers_filled = cleaned_sales["Publisher"].isna().sum()
    cleaned_sales["Publisher"] = cleaned_sales["Publisher"].fillna("Unknown")

    # With missing years removed, store years as whole numbers.
    cleaned_sales["Year"] = cleaned_sales["Year"].astype(int)

    # Keep all sales values, including zeros, and omit the DataFrame index.
    cleaned_sales.to_csv(output_file, index=False)

    print(f"Rows before cleaning: {rows_before:,}")
    print(f"Rows removed (missing Year): {rows_before - len(cleaned_sales):,}")
    print(f"Rows after cleaning: {len(cleaned_sales):,}")
    print(f"Missing publishers filled: {publishers_filled:,}")
    print(f"Saved cleaned data to: {output_file}")


if __name__ == "__main__":
    main()
