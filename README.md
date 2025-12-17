<<<<<<< HEAD
Bank Statements Processor API

This repository provides a FastAPI service that ingests bank statement CSVs, categorizes transactions, stores them in PostgreSQL (Docker), allows correcting a transaction's category, and lets you query transactions by category.

The input CSV for each bank must contain the expected bank-specific columns. See `constants/bank.py` for the enumerated columns per bank.
=======
# Bank Statements Processor

This repository is used to categorize bank transactions.

_Original Purpose_

This repository is still in progress. The first iteration of the repository was intended to be used with `python categorize_transactions.py <csv_in> [-o <csv_out>]`.
With the input CSV needing to contain at least these columns: Date, Description, Withdrawal, Deposit.

Currently working on improving the repository to have a use REST endpoints, have a db, etc.
>>>>>>> c7adda7e85f4a5f5002bbad3be05d71e8ad0e231

Endpoints

- POST `/transactions`: Upload a CSV and specify the bank; rows are categorized and saved.
- PATCH `/transactions/{id}/category`: Update `category` and/or `sub_category` for one transaction.
- GET `/transactions?category=...`: List all transactions for a given category.

Prerequisites

- Docker
- Python 3.9+

## Setup Instructions

### 1) Start PostgreSQL with Docker

```bash
docker compose up -d db
```

Wait for the database to be healthy (usually takes 5-10 seconds). Verify with:

```bash
docker compose ps
```

The database will be available on `localhost:5432` with database `money_categories`, user `postgres`, password `postgres`.

**Note:** If you encounter a "database does not exist" error, create it manually:

```bash
docker compose exec db psql -U postgres -d postgres -c "CREATE DATABASE money_categories;"
```

### 2) Install Python dependencies

**Option A: Using pip**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Option B: Using uv (optional)**

```bash
brew install uv
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3) Run the API

Make sure your virtual environment is activated, then start the server:

```bash
source .venv/bin/activate  # if not already activated
uvicorn src.main:app --reload
```

The default `DATABASE_URL` is already configured to connect to `postgresql+psycopg2://postgres:postgres@localhost:5432/money_categories`. If you need to override it:

```bash
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/money_categories
uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000` and interactive documentation at `http://127.0.0.1:8000/docs`.

On startup, the service ensures the `transactions` table exists with schema:

```
id SERIAL PK,
date DATE,
description TEXT,
withdrawal NUMERIC,
deposit NUMERIC,
category TEXT,
sub_category TEXT,
currency TEXT,
bank TEXT
```

Usage Examples

- Ingest a CSV (replace path and bank as appropriate; allowed values are defined in `Bank` enum, e.g. `schwab`, `lloyds`):

```
curl -X POST \
  -F "file=@/absolute/path/to/your.csv" \
  -F "bank=schwab" \
  http://127.0.0.1:8000/transactions
```

- Update category for a transaction:

```
curl -X PATCH \
  -F "category=Food" \
  -F "sub_category=Restaurants" \
  http://127.0.0.1:8000/transactions/123/category
```

- Get transactions by category:

```
curl "http://127.0.0.1:8000/transactions?category=Food"
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'constants'"**
- Make sure you're running from the project root directory
- Ensure `src/__init__.py` and `src/constants/__init__.py` exist (they should be created automatically)

**"Address already in use" error on port 8000**
- Stop any existing uvicorn processes: `pkill -f "uvicorn src.main:app"`
- Or stop the Docker app container: `docker compose stop app`

**"Database does not exist" error**
- Ensure the database container is running: `docker compose ps`
- Create the database manually if needed: `docker compose exec db psql -U postgres -d postgres -c "CREATE DATABASE money_categories;"`

**Import errors**
- Make sure your virtual environment is activated: `source .venv/bin/activate`
- Verify dependencies are installed: `pip list | grep fastapi`

## Notes

- The API normalizes amounts, strips currency symbols, and categorizes each row using the keyword maps in `constants/keywords.py`.
- If your CSV schema differs, adapt the `constants/bank.py` enums for `DATE`, `DESCRIPTION`, `WITHDRAWAL`, and `DEPOSIT`.
- The `transactions` table is automatically created on API startup if it doesn't exist.
