import argparse
import re
from pathlib import Path

import pandas as pd

from constants.keywords import KEYWORD_CATEGORY_MAPS
from constants.bank import SchwabColumns, Currency
# --------------------------------------------------------------------
# 1. Define category rules
# --------------------------------------------------------------------

def categorize(description: str) -> tuple[str, str]:
    """Return a category based on the transaction description."""
    
    # compare lower_desc and lower_keywords
    # todo: need to check if it's a deposit or withdrawal. 
    for obj in KEYWORD_CATEGORY_MAPS:
        category = obj["category"].value
        sub_category = obj["sub_category"].value
        keywords = obj["keywords"]

        text = description.lower()
        for keyword in keywords:
            if re.search(keyword.lower(), text):
                return category, sub_category
    return "Other", ""


# --------------------------------------------------------------------
# 2. Command‑line interface
# --------------------------------------------------------------------
def main(csv_in: str = "charles_schwab_example.csv", csv_out: str = "categorized.csv") -> None:
    """Read the CSV, add Category column, and write a new CSV."""
    print(f"Reading {csv_in}...")
    df = pd.read_csv(csv_in)

    # Guard against missing column
    desired_columns = [column.value for column in SchwabColumns]
    for col in desired_columns:
        if col not in df.columns:
            print('column not present')
            raise ValueError(f"Input CSV must contain a '{col}' column")
    # Only keep relevant columns
    print(desired_columns)
    df = df[desired_columns]

    # TODO: Delete rows where Description includes Transfer to Brokerage

    # Remove rows where Description is NaN
    # TODOJ: Handle Deposits later
    df = df.dropna(subset=["Withdrawal"])
    # Handle deposits:
    # VENMO
    # "IRS  TREASURY",
    # FRANCHISE TAX BD
    # "Interest Paid"
    # "Cuploop OU Tallin" - deposit

    # Categorize
    print("Categorizing transactions...")
    df[["Category", "SubCategory"]] = (
        df["Description"]
        .apply(categorize)
        .apply(pd.Series) # turns tuples into two columns
    )
    df["Currency"] = Currency.GBP.value

    # Write
    df.to_csv(csv_out, index=False)
    print(f"✔ Categorized file saved to {Path(csv_out).resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add a Category column to a transaction CSV"
    )
    parser.add_argument(
        "-i",
        "--csv_in",
        default="bank_csvs/charles_schwab_example.csv",
        help="Path to the input CSV file (default: bank_csvscharles_schwab_example.csv)"
    )
    parser.add_argument(
        "-o",
        "--csv_out",
        default="~/Downloads/categorized.csv",
        help="Output CSV path (default: ~/Downloads/categorized.csv)",
    )
    args = parser.parse_args()
    print(args)
    main(args.csv_in, args.csv_out)