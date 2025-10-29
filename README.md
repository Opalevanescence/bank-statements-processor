Categorize bank transactions.

Usage:
    python categorize_transactions.py <csv_in> [-o <csv_out>]

The input CSV must contain at least these columns:
    Date, Description, Withdrawal, Deposit


## Setup
Install Docker

```
docker compose up --build

```


```
brew install uv

# Create an environment
uv venv

# tell uv to treat current directory as a project with pyproject.toml as source of dependencies
# Note - i'm dubious this does what it says above
uv pip install --editable . 

# Add new dependencies to the project.toml file
# Dev flag will only add dependency to the dev list
uv add --dev <dependency>

# run using script
uv dev
```

# Create local PostgreSQL Instance

```
brew install postgresql
brew services start postgresql
createdb money-categories
```