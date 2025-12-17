import argparse
import os
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# logger = logging.getLogger(__name__)

from io import BytesIO
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Path, Query
from pathlib import Path
from sqlalchemy import create_engine, text

from .constants.keywords import KEYWORD_CATEGORY_MAPS
from .constants.bank import  Currency, Bank, LloydsColumns, SchwabColumns

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
app = FastAPI(title="Bank Statements API", version="1.0.0")

# Read database URL from env with a sensible default for local dev
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/money_categories"
)
engine = create_engine(DATABASE_URL)


def ensure_transactions_table_exists() -> None:
    create_sql = text(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id           SERIAL PRIMARY KEY,
            date         DATE,
            description  TEXT,
            withdrawal   NUMERIC,
            deposit      NUMERIC,
            category     TEXT,
            sub_category TEXT,
            currency     TEXT,
            bank         TEXT
        );
        """
    )
    with engine.begin() as conn:
        conn.execute(create_sql)


@app.on_event("startup")
def on_startup() -> None:
    ensure_transactions_table_exists()


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
    # Validate bank against enum, allowing case-insensitive names
    bank_key = bank.strip().upper()
    try:
        bank_enum = getattr(Bank, bank_key)
    except AttributeError:
        valid_values = ", ".join([m.name.lower() for m in Bank])
        raise HTTPException(status_code=400, detail=f"bank must be one of: {valid_values}")

    try:
        # Read CSV into DataFrame. We have the full content in memory; fine for < few MB.
        raw_bytes = await file.read()
        df = pd.read_csv(BytesIO(raw_bytes))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Malformed CSV: {exc}") from exc

    # Assign values based on bank
    if bank_enum == Bank.SCHWAB:
        columnsEnum = SchwabColumns 
        currency = Currency.USD.value
    else:
        columnsEnum = LloydsColumns
        currency = Currency.GBP.value
    
    # Basic column sanity‑check – expect these four canonical names.
    desired_columns = [column.value for column in columnsEnum]
    missing = [col for col in desired_columns if col not in df.columns]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing required columns: {missing} in {df.columns}")

    # Categorise using vectorised apply.
    df = df[desired_columns].copy()
    # Normalize amounts: strip $ and commas, convert to numeric (empty strings become NaN)
    if columnsEnum.WITHDRAWAL.value in df.columns:
        df[columnsEnum.WITHDRAWAL.value] = pd.to_numeric(
            df[columnsEnum.WITHDRAWAL.value]
            .replace(r"[\$,]", "", regex=True)
            .replace("", pd.NA),
            errors="coerce"
        )
    if columnsEnum.DEPOSIT.value in df.columns:
        df[columnsEnum.DEPOSIT.value] = pd.to_numeric(
            df[columnsEnum.DEPOSIT.value]
            .replace(r"[\$,]", "", regex=True)
            .replace("", pd.NA),
            errors="coerce"
        )
    df[["category", "sub_category"]] = (
        df[columnsEnum.DESCRIPTION.value].apply(categorize).apply(pd.Series)
    )
    df["currency"] = currency
    df["bank"] = bank_enum.name.lower()

    # Persist to PostgreSQL in a single bulk insert.
    #     to_sql emits INSERT … VALUES batches behind the scenes.
    try:
        with engine.begin() as conn:  # ensures commit/rollback
            # Align to DB schema
            insert_df = pd.DataFrame({
                "date": df[columnsEnum.DATE.value],
                "description": df[columnsEnum.DESCRIPTION.value],
                "withdrawal": df.get(columnsEnum.WITHDRAWAL.value),
                "deposit": df.get(columnsEnum.DEPOSIT.value),
                "category": df["category"],
                "sub_category": df["sub_category"],
                "currency": df["currency"],
                "bank": df["bank"],
            })
            insert_df.to_sql("transactions", conn, if_exists="append", index=False)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database insert failed: {exc}") from exc

    return {"inserted_rows": len(df)}


@app.patch(
    "/transactions/{transaction_id}/category",
    summary="Update category and/or sub_category for a transaction",
)
async def update_transaction_category(
    transaction_id: int = Path(description="Transaction id"),
    category: str = Form(default=None),
    sub_category: str = Form(default=None),
):
    if category is None and sub_category is None:
        raise HTTPException(status_code=400, detail="Provide category and/or sub_category")

    set_clauses = []
    params: dict[str, object] = {"id": transaction_id}
    if category is not None:
        set_clauses.append("category = :category")
        params["category"] = category
    if sub_category is not None:
        set_clauses.append("sub_category = :sub_category")
        params["sub_category"] = sub_category
    sql = text(f"UPDATE transactions SET {', '.join(set_clauses)} WHERE id = :id")

    with engine.begin() as conn:
        result = conn.execute(sql, params)
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")

    return {"updated": True, "id": transaction_id}


@app.get(
    "/transactions",
    summary="List transactions filtered by category",
)
async def list_transactions_by_category(
    category: str = Query(..., description="Category to filter by"),
):
    sql = text(
        """
        SELECT id, date, description, withdrawal, deposit, category, sub_category, currency, bank
        FROM transactions
        WHERE category = :category
        ORDER BY date NULLS LAST, id ASC
        """
    )
    with engine.begin() as conn:
        rows = conn.execute(sql, {"category": category}).mappings().all()
        return [dict(r) for r in rows]


# --------------------------------------------------------------------
# 2. Command‑line interface
# --------------------------------------------------------------------
# def main(csv_in: str = "charles_schwab_example.csv", csv_out: str = "categorized.csv") -> None:
#     """Read the CSV, add Category column, and write a new CSV."""
#     df = pd.read_csv(csv_in)

#     # Guard against missing column
#     desired_columns = [column.value for column in SchwabColumns]
#     for col in desired_columns:
#         if col not in df.columns:
#             print('column not present')
#             raise ValueError(f"Input CSV must contain a '{col}' column")
#     # Only keep relevant columns
#     df = df[desired_columns]
#     # Remove dollar signs and commas, then convert to float
#     df["Withdrawal"] = (
#         df["Withdrawal"]
#         .replace("[\$,]", "", regex=True)  # remove $ and commas
#         .astype(float)
#     )

#     # TODO: Delete rows where Description includes Transfer to Brokerage

#     # Remove rows where Description is NaN
#     # TODOJ: Handle Deposits later
#     df = df.dropna(subset=["Withdrawal"])
#     # Handle deposits:
#     # VENMO
#     # "IRS  TREASURY",
#     # FRANCHISE TAX BD
#     # "Interest Paid"
#     # "Cuploop OU Tallin" - deposit

#     # Categorize
#     print("Categorizing transactions...")
#     df[["Category", "SubCategory"]] = (
#         df["Description"]
#         .apply(categorize)
#         .apply(pd.Series) # turns tuples into two columns
#     )
#     df["Currency"] = Currency.GBP.value

#     # Write
#     df.to_csv(csv_out, index=False)
#     print(f"✔ Categorized file saved to {Path(csv_out).resolve()}")

#     # count_category_totals
#     df["Withdrawal"] = pd.to_numeric(df["Withdrawal"], errors="coerce")
#     category_totals = df.groupby("Category")["Withdrawal"].sum().reset_index()

#     print(category_totals)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="Add a Category column to a transaction CSV"
#     )
#     parser.add_argument(
#         "-i",
#         "--csv_in",
#         default="bank_csvs/charles_schwab_example.csv",
#         help="Path to the input CSV file (default: bank_csvscharles_schwab_example.csv)"
#     )
#     parser.add_argument(
#         "-o",
#         "--csv_out",
#         default="~/Downloads/categorized.csv",
#         help="Output CSV path (default: ~/Downloads/categorized.csv)",
#     )
#     args = parser.parse_args()
#     print(args)
#     main(args.csv_in, args.csv_out)