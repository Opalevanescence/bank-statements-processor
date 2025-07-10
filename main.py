import argparse
import os
import re

from io import BytesIO
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pathlib import Path
from sqlalchemy import create_engine

from constants.keywords import KEYWORD_CATEGORY_MAPS
from constants.bank import  Currency, Bank, LloydsColumns, SchwabColumns

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
#  FastAPI setup
# --------------------------------------------------------------------
app = FastAPI(title="Bank CSV Ingest", version="1.0.0")

# Read database URL from env with a sensible default for local dev
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
)
engine = create_engine(DATABASE_URL, future=True)


@app.post("/transactions", summary="Ingest a bank CSV and store rows.")
async def upload_transactions(
    file: UploadFile = File(description="Bank transactions CSV"),
    bank: str = Form(description="Source bank identifier (e.g. 'schwab')"),
):
    """
    Parse *file* as CSV, categorise rows, and bulk insert into PostgreSQL.

    Returns the count of inserted rows.
    """
    # Validate parameters
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")
    if bank not in Bank:
        raise HTTPException(status_code=400, detail=f"{bank} must be one of {list(Bank.value)}")

    try:
        # Read CSV into DataFrame. We have the full content in memory; fine for < few MB.
        raw_bytes = await file.read()
        df = pd.read_csv(BytesIO(raw_bytes))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Malformed CSV: {exc}") from exc

    # Assign values based on bank
    if bank == Bank.SCHWAB:
        columnsEnum = SchwabColumns 
        currency = Currency.USD.value
    else:
        columnsEnum = LloydsColumns
        currency = Currency.GBP.value
    
    # Basic column sanity‑check – expect these four canonical names.
    desired_columns = [column.value for column in columnsEnum]
    missing = desired_columns - set(df.columns)
    for col in desired_columns:
        if col not in df.columns:
            raise HTTPException(status_code=422, detail=f"Missing required columns: {missing}")

    # Categorise using vectorised apply.
    df = df[desired_columns]
    df[columnsEnum.WITHDRAWAL] = (
        df[columnsEnum.WITHDRAWAL]
        .replace("[\$]", "", regex=True)  # remove $
        .astype(float)
    )
    df[["category", "sub_category"]] = (
        df["Description"].apply(categorize).apply(pd.Series)
    )
    df["currency"] = currency
    df["bank"] = bank

    # Persist to PostgreSQL in a single bulk insert.
    #     to_sql emits INSERT … VALUES batches behind the scenes.
    try:
        with engine.begin() as conn:  # ensures commit/rollback
            df.to_sql("transactions", conn, if_exists="append", index=False)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {exc}") from exc

    return {"inserted_rows": len(df)}


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
    df = df[desired_columns]
    # Remove dollar signs and commas, then convert to float
    df["Withdrawal"] = (
        df["Withdrawal"]
        .replace("[\$,]", "", regex=True)  # remove $ and commas
        .astype(float)
    )

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

    # count_category_totals
    df["Withdrawal"] = pd.to_numeric(df["Withdrawal"], errors="coerce")
    category_totals = df.groupby("Category")["Withdrawal"].sum().reset_index()

    print(category_totals)

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