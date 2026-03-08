import os
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from io import BytesIO
import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Path, Query
from typing import Optional
from enum import Enum
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


def _enum_member_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()


CATEGORY_VALUES = sorted({obj["category"].value for obj in KEYWORD_CATEGORY_MAPS})
SUB_CATEGORY_VALUES = sorted({obj["sub_category"].value for obj in KEYWORD_CATEGORY_MAPS})

CategoryOption = Enum(
    "CategoryOption",
    {_enum_member_name(value): value for value in CATEGORY_VALUES},
)
SubCategoryOption = Enum(
    "SubCategoryOption",
    {_enum_member_name(value): value for value in SUB_CATEGORY_VALUES},
)

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
        CREATE TABLE IF NOT EXISTS banks (
            id       SERIAL PRIMARY KEY,
            name     TEXT UNIQUE,
            currency TEXT
        );

        CREATE TABLE IF NOT EXISTS categories (
            id           SERIAL PRIMARY KEY,
            sub_category TEXT,
            category     TEXT,
            UNIQUE (category, sub_category)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id              SERIAL PRIMARY KEY,
            date            DATE,
            description     TEXT,
            withdrawal      NUMERIC,
            deposit         NUMERIC,
            sub_category_id INTEGER REFERENCES categories(id),
            bank_id         INTEGER REFERENCES banks(id)
        );
        """
    )
    with engine.begin() as conn:
        conn.execute(create_sql)


def get_or_create_bank(conn, name: str, currency: str) -> int:
    select_sql = text("SELECT id FROM banks WHERE name = :name")
    insert_sql = text("INSERT INTO banks (name, currency) VALUES (:name, :currency)")
    row = conn.execute(select_sql, {"name": name}).fetchone()
    if row:
        return row[0]
    conn.execute(insert_sql, {"name": name, "currency": currency})
    row = conn.execute(select_sql, {"name": name}).fetchone()
    return row[0]


def get_or_create_category(conn, category: str, sub_category: str) -> int:
    select_sql = text(
        """
        SELECT id FROM categories
        WHERE category = :category AND sub_category = :sub_category
        """
    )
    insert_sql = text(
        """
        INSERT INTO categories (category, sub_category)
        VALUES (:category, :sub_category)
        """
    )
    params = {"category": category, "sub_category": sub_category}
    row = conn.execute(select_sql, params).fetchone()
    if row:
        return row[0]
    conn.execute(insert_sql, params)
    row = conn.execute(select_sql, params).fetchone()
    return row[0]


@app.on_event("startup")
def on_startup() -> None:
    ensure_transactions_table_exists()


@app.post("/transactions", summary="Ingest a bank CSV and store rows.")
async def upload_transactions(
    file: UploadFile = File(description="Bank transactions CSV"),
    bank: Bank = Form(description="Source bank identifier"),
):
    """
    Parse *file* as CSV, categorise rows, and bulk insert into PostgreSQL.

    Returns the count of inserted rows.
    """
    # Validate parameters
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")
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
    missing = [col for col in desired_columns if col not in df.columns]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing required columns: {missing} in {df.columns}")

    # Categorise using vectorised apply.
    df = df[desired_columns].copy()
    # Normalize dates per bank format
    date_format = "%m/%d/%Y" if bank == Bank.SCHWAB else "%d/%m/%Y"
    df[columnsEnum.DATE.value] = pd.to_datetime(
        df[columnsEnum.DATE.value],
        format=date_format,
        errors="coerce",
    ).dt.date
    invalid_date_count = df[columnsEnum.DATE.value].isna().sum()
    if invalid_date_count:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid date format for {invalid_date_count} row(s). "
                f"Expected format {date_format} for bank {bank.value}."
            ),
        )
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

    # Persist to PostgreSQL in a single bulk insert.
    #     to_sql emits INSERT … VALUES batches behind the scenes.
    try:
        with engine.begin() as conn:  # ensures commit/rollback
            bank_id = get_or_create_bank(conn, bank.value, currency)

            category_pairs = (
                df[["category", "sub_category"]]
                .fillna("")
                .drop_duplicates()
                .to_records(index=False)
            )
            category_map: dict[tuple[str, str], int] = {}
            for category_value, sub_category_value in category_pairs:
                category_id = get_or_create_category(
                    conn, category_value, sub_category_value
                )
                category_map[(category_value, sub_category_value)] = category_id

            df["sub_category_id"] = df.apply(
                lambda row: category_map.get(
                    (row["category"], row["sub_category"]), None
                ),
                axis=1,
            )

            # Align to DB schema
            insert_df = pd.DataFrame({
                "date": df[columnsEnum.DATE.value],
                "description": df[columnsEnum.DESCRIPTION.value],
                "withdrawal": df.get(columnsEnum.WITHDRAWAL.value),
                "deposit": df.get(columnsEnum.DEPOSIT.value),
                "sub_category_id": df["sub_category_id"],
                "bank_id": bank_id,
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
    category: Optional[CategoryOption] = Form(default=None),
    sub_category: Optional[SubCategoryOption] = Form(default=None),
):
    if category is None and sub_category is None:
        raise HTTPException(status_code=400, detail="Provide category and/or sub_category")

    with engine.begin() as conn:
        existing = conn.execute(
            text(
                """
                SELECT t.id, c.category, c.sub_category
                FROM transactions t
                LEFT JOIN categories c ON t.sub_category_id = c.id
                WHERE t.id = :id
                """
            ),
            {"id": transaction_id},
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Transaction not found")

        current_category = existing[1] or ""
        current_sub_category = existing[2] or ""
        new_category = category.value if category is not None else current_category
        new_sub_category = (
            sub_category.value if sub_category is not None else current_sub_category
        )

        new_category_id = get_or_create_category(conn, new_category, new_sub_category)
        conn.execute(
            text("UPDATE transactions SET sub_category_id = :sid WHERE id = :id"),
            {"sid": new_category_id, "id": transaction_id},
        )

    return {
        "updated": True,
        "id": transaction_id,
        "category": new_category,
        "sub_category": new_sub_category,
    }


@app.delete(
    "/transactions/{transaction_id}",
    summary="Delete a transaction by id",
)
async def delete_transaction(
    transaction_id: int = Path(description="Transaction id"),
):
    with engine.begin() as conn:
        result = conn.execute(
            text("DELETE FROM transactions WHERE id = :id"),
            {"id": transaction_id},
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")

    return {"deleted": True, "id": transaction_id}


@app.get(
    "/transactions/summary",
    summary="Summarize totals by category and sub-category",
)
async def get_transactions_summary(
    start_date: Optional[str] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD)"),
):
    clauses = []
    params: dict[str, object] = {}
    if start_date:
        clauses.append("t.date >= :start_date")
        params["start_date"] = start_date
    if end_date:
        clauses.append("t.date <= :end_date")
        params["end_date"] = end_date
    where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    sql = text(
        f"""
        SELECT
            COALESCE(c.category, 'Uncategorized') AS category,
            COALESCE(c.sub_category, 'Uncategorized') AS sub_category,
            COALESCE(SUM(t.withdrawal), 0) AS total_withdrawal,
            COALESCE(SUM(t.deposit), 0) AS total_deposit
        FROM transactions t
        LEFT JOIN categories c ON t.sub_category_id = c.id
        {where_clause}
        GROUP BY c.category, c.sub_category
        ORDER BY c.category, c.sub_category
        """
    )
    with engine.begin() as conn:
        rows = conn.execute(sql, params).mappings().all()

    summary: dict[str, dict[str, dict[str, float]]] = {}
    totals: dict[str, dict[str, float]] = {}
    for row in rows:
        category_name = row["category"]
        sub_category_name = row["sub_category"]
        total_withdrawal = float(row["total_withdrawal"] or 0)
        total_deposit = float(row["total_deposit"] or 0)

        if category_name not in summary:
            summary[category_name] = {}
            totals[category_name] = {"total_withdrawal": 0.0, "total_deposit": 0.0}

        summary[category_name][sub_category_name] = {
            "total_withdrawal": total_withdrawal,
            "total_deposit": total_deposit,
        }
        totals[category_name]["total_withdrawal"] += total_withdrawal
        totals[category_name]["total_deposit"] += total_deposit

    for category_name, totals_obj in totals.items():
        summary[category_name]["total"] = totals_obj

    return summary


@app.get(
    "/transactions",
    summary="List transactions filtered by category and date range",
)
async def list_transactions(
    category: Optional[CategoryOption] = Query(default=None, description="Category to filter by"),
    sub_category: Optional[SubCategoryOption] = Query(default=None, description="Sub-category to filter by"),
    start_date: Optional[str] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD)"),
):
    clauses = []
    params: dict[str, object] = {}
    if category:
        clauses.append("c.category = :category")
        params["category"] = category.value
    if sub_category:
        clauses.append("c.sub_category = :sub_category")
        params["sub_category"] = sub_category.value
    if start_date:
        clauses.append("t.date >= :start_date")
        params["start_date"] = start_date
    if end_date:
        clauses.append("t.date <= :end_date")
        params["end_date"] = end_date

    where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = text(
        f"""
        SELECT
            t.id,
            t.date,
            t.description,
            t.withdrawal,
            t.deposit,
            c.category,
            c.sub_category,
            b.name AS bank,
            b.currency
        FROM transactions t
        LEFT JOIN categories c ON t.sub_category_id = c.id
        LEFT JOIN banks b ON t.bank_id = b.id
        {where_clause}
        ORDER BY t.date NULLS LAST, t.id ASC
        """
    )
    with engine.begin() as conn:
        rows = conn.execute(sql, params).mappings().all()
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