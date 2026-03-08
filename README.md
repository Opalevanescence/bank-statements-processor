# Bank Statements Processor

This repository is used to categorize bank transactions.

_Original Purpose_

This repository is still in progress. The first iteration of the repository was intended to be used with `python categorize_transactions.py <csv_in> [-o <csv_out>]`.
With the input CSV needing to contain at least these columns: Date, Description, Withdrawal, Deposit.

Currently working on improving the repository to have a use REST endpoints, have a db, etc.

Endpoints

- POST `/transactions`: Upload a CSV and specify the bank; rows are categorized and saved.
- PATCH `/transactions/{id}/category`: Update `category` and/or `sub_category` for one transaction.
- GET `/transactions`: List transactions filtered by optional query params:
  `category`, `sub_category`, `start_date`, `end_date`. If no params are passed, all transactions are returned.
- GET `/transactions/summary`: Summarize totals by category and sub-category for an optional date range.
- DELETE `/transactions/{id}`: Delete a transaction.

Prerequisites

- Docker
- Python 3.9+

## Setup Instructions

### 1) Start PostgreSQL and Metabase with Docker

```bash
docker compose up -d db metabase
```

Wait for the database to be healthy (usually takes 5-10 seconds). Verify with:

```bash
docker compose ps
```

The database will be available on `localhost:5432` with database `money_categories`, user `postgres`, password `postgres`.

**Metabase** will be available at `http://localhost:3000`. On first visit, complete the setup wizard, then add the database:

- **Admin** → **Databases** → **Add database**
- **Database type:** PostgreSQL
- **Host:** `db` (use this when Metabase runs via Docker Compose; it resolves to the Postgres container)
- **Port:** `5432`
- **Database name:** `money_categories`
- **Username:** `postgres`
- **Password:** `postgres`

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

On startup, the service ensures the database tables exist with schema:

```
banks:
  id SERIAL PK,
  name TEXT UNIQUE,
  currency TEXT

categories:
  id SERIAL PK,
  sub_category TEXT,
  category TEXT,
  UNIQUE (category, sub_category)

transactions:
  id SERIAL PK,
  date DATE,
  description TEXT,
  withdrawal NUMERIC,
  deposit NUMERIC,
  sub_category_id INTEGER,
  bank_id INTEGER
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

- Get transactions in a date range:

```
curl "http://127.0.0.1:8000/transactions?start_date=2024-01-01&end_date=2024-01-31"
```

- Get a summary by category/sub-category:

```
curl "http://127.0.0.1:8000/transactions/summary?start_date=2024-01-01&end_date=2024-01-31"
```

- Delete a transaction:

```
curl -X DELETE "http://127.0.0.1:8000/transactions/123"
```

## Troubleshooting

**"ModuleNotFoundError: No module named 'constants'"**
- Make sure you're running from the project root directory
- Ensure `src/__init__.py` and `src/constants/__init__.py` exist (they should be created automatically)

**"Address already in use" error on port 8000**
- Stop any existing server processes: `pkill -f "uvicorn src.main:app"`
- Or stop the Docker app container: `docker compose stop app`

**"Database does not exist" error**
- Ensure the database container is running: `docker compose ps`
- Create the database manually if needed: `docker compose exec db psql -U postgres -d postgres -c "CREATE DATABASE money_categories;"`
- If you changed schemas, reset the DB:
  `docker compose down -v && docker compose up -d db`

**Import errors**
- Make sure your virtual environment is activated: `source .venv/bin/activate`
- Verify dependencies are installed: `pip list | grep fastapi`

## Notes

- The API normalizes amounts, strips currency symbols, and categorizes each row using the keyword maps in `constants/keywords.py`.
- If your CSV schema differs, adapt the `constants/bank.py` enums for `DATE`, `DESCRIPTION`, `WITHDRAWAL`, and `DEPOSIT`.
- Schwab CSV dates are parsed as `MM/DD/YYYY`; Lloyds dates are parsed as `DD/MM/YYYY`.
- The database tables are automatically created on API startup if they don't exist.
- In the docs UI, `bank`, `category`, and `sub_category` are restricted to known values via drop-downs.
